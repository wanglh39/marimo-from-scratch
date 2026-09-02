"""App 类：让 .py notebook 文件可直接 `python notebook.py` 运行。

序列化生成的 .py 文件末尾包含：
    if __name__ == "__main__":
        app.run()

App.cell 装饰器收集所有 cell 函数，run() 时提取信息、构建图、执行。
"""

from __future__ import annotations

import ast
import inspect
import textwrap

from .core import Cell, CellGraph, CellStatus, Executor


class App:
    def __init__(self) -> None:
        self._funcs: list = []

    def cell(self, func):
        self._funcs.append(func)
        return func

    def run(self) -> None:
        graph = self._build_graph()
        executor = Executor(graph)
        from .components import ui as ui_module
        executor.inject("ui", ui_module)
        executor.run_all()
        self._print_results(graph)

    def _build_graph(self) -> CellGraph:
        graph = CellGraph()
        for i, func in enumerate(self._funcs):
            source = textwrap.dedent(inspect.getsource(func))
            func_def = ast.parse(source).body[0]

            refs = {arg.arg for arg in func_def.args.args}
            defs = _extract_return_defs(func_def)
            code = _extract_body_code(func_def)

            cell = Cell(cell_id=f"cell_{i}", code=code, defs=defs, refs=refs)
            graph.add_cell(cell)
        return graph

    def _print_results(self, graph: CellGraph) -> None:
        print("=" * 60)
        for cell_id in graph.topological_order():
            cell = graph.get_cell(cell_id)
            icon = {
                CellStatus.DONE: "✓",
                CellStatus.ERROR: "✗",
                CellStatus.STALE: "○",
            }.get(cell.status, "·")
            print(f"\n[{icon}] cell {cell_id}")
            print(f"    code: {cell.code!r}")
            if cell.stdout:
                print(f"    stdout: {cell.stdout.strip()}")
            if cell.output is not None:
                print(f"    output: {cell.output!r}")
            if cell.exception:
                print(f"    error: {type(cell.exception).__name__}: {cell.exception}")
        print("=" * 60)


def _extract_return_defs(func_def: ast.FunctionDef) -> set[str]:
    for stmt in reversed(func_def.body):
        if isinstance(stmt, ast.Return):
            if stmt.value is None:
                return set()
            if isinstance(stmt.value, ast.Name):
                return {stmt.value.id}
            if isinstance(stmt.value, ast.Tuple):
                return {
                    elt.id for elt in stmt.value.elts if isinstance(elt, ast.Name)
                }
    return set()


def _extract_body_code(func_def: ast.FunctionDef) -> str:
    code_stmts = [s for s in func_def.body if not isinstance(s, ast.Return)]
    if not code_stmts:
        return ""
    return "\n".join(ast.unparse(stmt) for stmt in code_stmts)