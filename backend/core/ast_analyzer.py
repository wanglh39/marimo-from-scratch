"""AST 依赖分析器：从 cell 代码中静态提取定义和引用的变量。

这是 reactive 系统的基础——无需运行代码，仅靠静态分析就能确定 cell 间的
依赖关系。提取两类信息：
  - defs：cell 在顶层作用域绑定的变量名（赋值、函数定义、导入等）
  - refs：cell 引用的外部变量名（所有读取，减去函数内部局部变量）

构建 DAG 时，若 cell A 的 defs ∩ cell B 的 refs ≠ ∅，则 B 依赖 A。

简化说明（教学版）：
  - 星号导入 (from m import *) 无法静态分析，暂跳过
  - global / nonlocal 声明未特殊处理
  - del 语句未计入 refs
"""

from __future__ import annotations

import ast
import builtins


class AnalysisError(Exception):
    pass


_BUILTIN_NAMES = set(dir(builtins))


def analyze_cell(code: str) -> tuple[set[str], set[str]]:
    if not code.strip():
        return set(), set()
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise AnalysisError(f"语法错误: {e.msg} (行 {e.lineno})") from e
    defs = _extract_top_level_defs(tree)
    refs = _extract_refs(tree, defs)
    return defs, refs


def _extract_top_level_defs(tree: ast.Module) -> set[str]:
    defs: set[str] = set()
    for stmt in tree.body:
        defs |= _extract_bindings(stmt)
    return defs


def _extract_bindings(stmt: ast.stmt) -> set[str]:
    bindings: set[str] = set()

    if isinstance(stmt, ast.Assign):
        for target in stmt.targets:
            bindings |= _extract_target_names(target)
    elif isinstance(stmt, ast.AnnAssign) and stmt.target is not None:
        bindings |= _extract_target_names(stmt.target)
    elif isinstance(stmt, ast.AugAssign):
        bindings |= _extract_target_names(stmt.target)
    elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        bindings.add(stmt.name)
    elif isinstance(stmt, ast.Import):
        for alias in stmt.names:
            bindings.add(alias.asname or alias.name.split(".")[0])
    elif isinstance(stmt, ast.ImportFrom):
        for alias in stmt.names:
            if alias.name == "*":
                continue
            bindings.add(alias.asname or alias.name)
    elif isinstance(stmt, (ast.For, ast.AsyncFor)):
        bindings |= _extract_target_names(stmt.target)
    elif isinstance(stmt, (ast.With, ast.AsyncWith)):
        for item in stmt.items:
            if item.optional_vars is not None:
                bindings |= _extract_target_names(item.optional_vars)
    elif isinstance(stmt, ast.NamedExpr):
        bindings |= _extract_target_names(stmt.target)
    elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.NamedExpr):
        bindings |= _extract_target_names(stmt.value.target)

    return bindings


def _extract_target_names(target: ast.expr) -> set[str]:
    names: set[str] = set()
    if isinstance(target, ast.Name):
        names.add(target.id)
    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            names |= _extract_target_names(elt)
    elif isinstance(target, ast.Starred):
        names |= _extract_target_names(target.value)
    return names


def _extract_refs(tree: ast.Module, defs: set[str]) -> set[str]:
    all_loads: set[str] = set()
    all_stores: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                all_loads.add(node.id)
            elif isinstance(node.ctx, ast.Store):
                all_stores.add(node.id)
        elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
            all_loads.add(node.target.id)

    internal_locals = all_stores - defs
    return (all_loads - internal_locals) - _BUILTIN_NAMES