"""Cell 数据结构：reactive notebook 的最小计算单元。

一个 Cell 对应 notebook 中的一个代码块。它同时携带两类信息：
  1. 静态信息 —— code、defs（定义的变量）、uses（使用的变量），
     其中 defs / uses 由 AST 分析器填充，用于构建依赖图。
  2. 运行时状态 —— status、output、stdout、exception、namespace，
     由执行引擎在每次运行后更新。

namespace 记录该 cell 执行后产出的变量值，下游 cell 通过它获取依赖。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CellStatus(Enum):
    IDLE = "idle"
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    STALE = "stale"


@dataclass
class Cell:
    cell_id: str
    code: str
    defs: set[str] = field(default_factory=set)
    refs: set[str] = field(default_factory=set)

    status: CellStatus = CellStatus.IDLE
    output: Any = None
    stdout: str = ""
    exception: BaseException | None = None
    namespace: dict[str, Any] = field(default_factory=dict)

    def reset_runtime_state(self) -> None:
        self.status = CellStatus.IDLE
        self.output = None
        self.stdout = ""
        self.exception = None
        self.namespace = {}

    def mark_stale(self) -> None:
        self.status = CellStatus.STALE
        self.output = None
        self.stdout = ""
        self.exception = None
        self.namespace = {}

    @property
    def has_error(self) -> bool:
        return self.status is CellStatus.ERROR

    @property
    def is_runnable(self) -> bool:
        return self.status in (CellStatus.IDLE, CellStatus.PENDING, CellStatus.STALE)