"""解析：.py 文件文本 → CellGraph。

从被 @app.cell 装饰的函数中提取 cell 信息：
  - 函数参数 → refs
  - return 语句中的变量名 → defs
  - 函数体（去掉 return）→ cell 代码
"""

from __future__ import annotations

import ast

from ..core import Cell, CellGraph


class ParseError(Exception):
    pass


def py_to_graph(source: str) -> CellGraph:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ParseError(f"语法错误: {e.msg} (行 {e.lineno})") from e

    graph = CellGraph()
    cell_index = 0

    for stmt in tree.body:
        if not isinstance(stmt, ast.FunctionDef):
            continue
        if not _has_cell_decorator(stmt):
            continue

        refs = {arg.arg for arg in stmt.args.args}
        defs = _extract_return_defs(stmt)
        code = _extract_body_code(stmt)

        cell_id = f"cell_{cell_index}"
        cell = Cell(cell_id=cell_id, code=code, defs=defs, refs=refs)
        graph.add_cell(cell)
        cell_index += 1

    return graph


def _has_cell_decorator(func: ast.FunctionDef) -> bool:
    for dec in func.decorator_list:
        if isinstance(dec, ast.Attribute) and dec.attr == "cell":
            return True
    return False


def _extract_return_defs(func: ast.FunctionDef) -> set[str]:
    for stmt in reversed(func.body):
        if isinstance(stmt, ast.Return):
            if stmt.value is None:
                return set()
            return _names_from_return_value(stmt.value)
    return set()


def _names_from_return_value(value: ast.expr) -> set[str]:
    if isinstance(value, ast.Name):
        return {value.id}
    if isinstance(value, ast.Tuple):
        return {
            elt.id for elt in value.elts if isinstance(elt, ast.Name)
        }
    return set()


def _extract_body_code(func: ast.FunctionDef) -> str:
    code_stmts = [s for s in func.body if not isinstance(s, ast.Return)]
    if not code_stmts:
        return ""
    return "\n".join(ast.unparse(stmt) for stmt in code_stmts)