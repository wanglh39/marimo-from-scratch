"""UI 组件：Python 对象 ↔ 前端控件，值变化触发 reactive 重跑。

使用方式（在 notebook cell 中）：
    s = ui.slider(0, 100, value=50)    # 创建 slider
    print(s.value)                      # 读取当前值

    # 另一个 cell：
    result = s.value * 2                # 依赖 s，s 变化时自动重跑

交互流程：
  1. cell 执行后，executor 扫描 namespace 中的 UIComponent，
     设置 component_id 为 "cell_id:var_name"
  2. 前端渲染组件，用户交互 → 发送 ui_event(component_id, new_value)
  3. session 更新组件值 → 重跑依赖该 cell 的后代 cell
"""

from __future__ import annotations

from typing import Any


class UIComponent:
    def __init__(
        self,
        component_type: str,
        initial_value: Any,
        props: dict[str, Any] | None = None,
    ) -> None:
        self.component_id: str | None = None
        self.component_type = component_type
        self._value = initial_value
        self.props = props or {}

    @property
    def value(self) -> Any:
        return self._value

    def set_value(self, new_value: Any) -> None:
        self._value = new_value

    def to_dict(self) -> dict[str, Any]:
        return {
            "_ui": True,
            "id": self.component_id,
            "type": self.component_type,
            "value": self._value,
            "props": self.props,
        }

    def __repr__(self) -> str:
        return f"{self.component_type}(value={self._value!r})"


class Slider(UIComponent):
    def __init__(
        self, min_val: float = 0, max_val: float = 100, step: float = 1, value: float = 50
    ) -> None:
        super().__init__(
            "slider",
            value,
            {"min": min_val, "max": max_val, "step": step},
        )


class Button(UIComponent):
    def __init__(self, label: str = "Click", value: int = 0) -> None:
        super().__init__("button", value, {"label": label})


class Checkbox(UIComponent):
    def __init__(self, label: str = "", value: bool = False) -> None:
        super().__init__("checkbox", value, {"label": label})


def slider(
    min_val: float = 0, max_val: float = 100, step: float = 1, value: float = 50
) -> Slider:
    return Slider(min_val, max_val, step, value)


def button(label: str = "Click") -> Button:
    return Button(label, 0)


def checkbox(label: str = "", value: bool = False) -> Checkbox:
    return Checkbox(label, value)