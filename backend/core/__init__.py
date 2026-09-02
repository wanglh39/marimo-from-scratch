"""core: 核心执行引擎 —— Cell 抽象、AST 依赖分析、DAG 构建、响应式执行。"""

from __future__ import annotations

from .ast_analyzer import AnalysisError, analyze_cell
from .cell import Cell, CellStatus
from .executor import Executor
from .graph import (
    CellGraph,
    CyclicDependencyError,
    DuplicateDefinitionError,
    GraphError,
)


def create_cell(cell_id: str, code: str) -> Cell:
    defs, refs = analyze_cell(code)
    return Cell(cell_id=cell_id, code=code, defs=defs, refs=refs)


__all__ = [
    "Cell",
    "CellStatus",
    "CellGraph",
    "Executor",
    "create_cell",
    "analyze_cell",
    "AnalysisError",
    "GraphError",
    "DuplicateDefinitionError",
    "CyclicDependencyError",
]
