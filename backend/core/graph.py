"""DAG 构建：基于 cell 的 defs / refs 构建有向无环图。

图的语义：边 A → B 表示「cell A 定义了 cell B 引用的变量」，
即 B 依赖 A，A 必须先执行。

核心查询：
  - predecessors: 直接上游
  - descendants:  所有后代（传递依赖的下游）—— 增量执行的关键
  - topological_order: 全局执行顺序
  - execution_order_from: 某个 cell 及其后代的执行顺序 —— 增量执行用
"""

from __future__ import annotations

from collections import defaultdict, deque

from .cell import Cell


class GraphError(Exception):
    pass


class DuplicateDefinitionError(GraphError):
    pass


class CyclicDependencyError(GraphError):
    pass


class CellGraph:
    def __init__(self) -> None:
        self._cells: dict[str, Cell] = {}
        self._downstream: dict[str, set[str]] = defaultdict(set)
        self._upstream: dict[str, set[str]] = defaultdict(set)

    @property
    def cells(self) -> dict[str, Cell]:
        return dict(self._cells)

    @property
    def cell_ids(self) -> set[str]:
        return set(self._cells)

    def get_cell(self, cell_id: str) -> Cell:
        if cell_id not in self._cells:
            raise GraphError(f"cell '{cell_id}' 不存在")
        return self._cells[cell_id]

    def add_cell(self, cell: Cell) -> None:
        if cell.cell_id in self._cells:
            raise GraphError(f"cell '{cell.cell_id}' 已存在")
        self._cells[cell.cell_id] = cell
        self._rebuild()

    def remove_cell(self, cell_id: str) -> None:
        if cell_id not in self._cells:
            raise GraphError(f"cell '{cell_id}' 不存在")
        del self._cells[cell_id]
        self._rebuild()

    def _rebuild(self) -> None:
        self._downstream = defaultdict(set)
        self._upstream = defaultdict(set)

        var_to_cell: dict[str, str] = {}
        for cell_id, cell in self._cells.items():
            for var in cell.defs:
                if var in var_to_cell:
                    raise DuplicateDefinitionError(
                        f"变量 '{var}' 同时定义于 cell "
                        f"'{var_to_cell[var]}' 和 '{cell_id}'"
                    )
                var_to_cell[var] = cell_id

        for cell_id, cell in self._cells.items():
            for var in cell.refs:
                upstream_id = var_to_cell.get(var)
                if upstream_id is not None and upstream_id != cell_id:
                    self._downstream[upstream_id].add(cell_id)
                    self._upstream[cell_id].add(upstream_id)

    def predecessors(self, cell_id: str) -> set[str]:
        return set(self._upstream.get(cell_id, set()))

    def successors(self, cell_id: str) -> set[str]:
        return set(self._downstream.get(cell_id, set()))

    def descendants(self, cell_id: str) -> set[str]:
        return self._bfs(cell_id, self._downstream)

    def ancestors(self, cell_id: str) -> set[str]:
        return self._bfs(cell_id, self._upstream)

    def _bfs(self, start: str, adj: dict[str, set[str]]) -> set[str]:
        visited: set[str] = set()
        queue: deque[str] = deque(adj.get(start, set()))
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            queue.extend(adj.get(node, set()))
        return visited

    def topological_order(self) -> list[str]:
        in_degree = {
            cid: len(self._upstream.get(cid, set())) for cid in self._cells
        }
        queue = deque(sorted(cid for cid, d in in_degree.items() if d == 0))
        order: list[str] = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for ds in sorted(self._downstream.get(node, set())):
                in_degree[ds] -= 1
                if in_degree[ds] == 0:
                    queue.append(ds)
        if len(order) != len(self._cells):
            remaining = set(self._cells) - set(order)
            raise CyclicDependencyError(
                f"检测到循环依赖，涉及 cell: {sorted(remaining)}"
            )
        return order

    def execution_order_from(self, cell_id: str) -> list[str]:
        affected = self.descendants(cell_id) | {cell_id}
        return self._topological_sort_subset(affected)

    def _topological_sort_subset(self, subset: set[str]) -> list[str]:
        in_degree = {
            cid: len(self._upstream.get(cid, set()) & subset) for cid in subset
        }
        queue = deque(sorted(cid for cid, d in in_degree.items() if d == 0))
        order: list[str] = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for ds in sorted(self._downstream.get(node, set()) & subset):
                in_degree[ds] -= 1
                if in_degree[ds] == 0:
                    queue.append(ds)
        return order