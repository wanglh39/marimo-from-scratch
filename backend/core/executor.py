"""执行引擎：按拓扑顺序执行 cell，支持增量执行与短路。

核心机制：
  - 全局命名空间 _global_ns：所有 cell 共享，按拓扑顺序执行时，
    上游 cell 定义的变量自然对下游可见。
  - 增量执行 run_cell：仅执行目标 cell 及其所有后代（descendants），
    未受影响的 cell 不重新执行。
  - 短路：某 cell 出错后，其所有后代标记为 STALE，不执行。
  - output 提取：若最后一条语句是表达式，其值作为 cell 输出（notebook 显示用）。
"""

from __future__ import annotations

import ast
import contextlib
import io
from typing import Any

from .cell import Cell, CellStatus
from .graph import CellGraph


class Executor:
    def __init__(self, graph: CellGraph) -> None:
        self._graph = graph
        self._base_ns: dict[str, Any] = {}
        self._global_ns: dict[str, Any] = {}
        self._cell_defs_cache: dict[str, set[str]] = {}

    @property
    def global_namespace(self) -> dict[str, Any]:
        return dict(self._global_ns)

    def inject(self, name: str, value: Any) -> None:
        self._base_ns[name] = value
        self._global_ns[name] = value

    def run_all(self) -> list[str]:
        self._global_ns = dict(self._base_ns)
        self._cell_defs_cache = {}
        order = self._graph.topological_order()
        executed: list[str] = []
        short_circuited = False
        for cell_id in order:
            cell = self._graph.get_cell(cell_id)
            if short_circuited or self._has_failed_upstream(cell_id):
                cell.mark_stale()
                continue
            self._execute_cell(cell)
            executed.append(cell_id)
            if cell.has_error:
                short_circuited = True
        return executed

    def run_cell(self, cell_id: str) -> list[str]:
        order = self._graph.execution_order_from(cell_id)
        for cid in order:
            self._cleanup_cell_vars(cid)

        executed: list[str] = []
        short_circuited = False
        for cid in order:
            cell = self._graph.get_cell(cid)
            if short_circuited or self._has_failed_upstream(cid):
                cell.mark_stale()
                continue
            self._execute_cell(cell)
            executed.append(cid)
            if cell.has_error:
                short_circuited = True
        return executed

    def run_descendants(self, cell_id: str) -> list[str]:
        descendants = self._graph.descendants(cell_id)
        if not descendants:
            return []
        order = self._graph._topological_sort_subset(descendants)
        for cid in order:
            self._cleanup_cell_vars(cid)

        executed: list[str] = []
        short_circuited = False
        for cid in order:
            cell = self._graph.get_cell(cid)
            if short_circuited or self._has_failed_upstream(cid):
                cell.mark_stale()
                continue
            self._execute_cell(cell)
            executed.append(cid)
            if cell.has_error:
                short_circuited = True
        return executed

    def _has_failed_upstream(self, cell_id: str) -> bool:
        for up_id in self._graph.predecessors(cell_id):
            up_cell = self._graph.get_cell(up_id)
            if up_cell.status in (CellStatus.ERROR, CellStatus.STALE):
                return True
        return False

    def _cleanup_cell_vars(self, cell_id: str) -> None:
        for var in self._cell_defs_cache.get(cell_id, set()):
            self._global_ns.pop(var, None)

    def _execute_cell(self, cell: Cell) -> None:
        cell.status = CellStatus.RUNNING
        cell.exception = None
        cell.stdout = ""
        cell.output = None

        try:
            tree = ast.parse(cell.code)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                if tree.body and isinstance(tree.body[-1], ast.Expr):
                    rest = ast.Module(
                        body=tree.body[:-1], type_ignores=tree.type_ignores
                    )
                    last = ast.Expression(body=tree.body[-1].value)
                    exec(
                        compile(rest, f"<cell:{cell.cell_id}>", "exec"),
                        self._global_ns,
                    )
                    cell.output = eval(
                        compile(last, f"<cell:{cell.cell_id}>", "eval"),
                        self._global_ns,
                    )
                else:
                    exec(
                        compile(tree, f"<cell:{cell.cell_id}>", "exec"),
                        self._global_ns,
                    )
            cell.stdout = buf.getvalue()
            cell.namespace = {
                var: self._global_ns[var]
                for var in cell.defs
                if var in self._global_ns
            }
            self._cell_defs_cache[cell.cell_id] = set(cell.defs)
            cell.status = CellStatus.DONE
        except Exception as e:
            cell.exception = e
            cell.namespace = {}
            self._cell_defs_cache[cell.cell_id] = set()
            cell.status = CellStatus.ERROR