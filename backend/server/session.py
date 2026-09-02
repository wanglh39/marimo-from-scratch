"""NotebookSession：管理一个 notebook 会话，处理客户端消息。

每个 WebSocket 连接对应一个独立的 NotebookSession，持有自己的
CellGraph + Executor。所有客户端消息经 handle_message 分发处理，
返回需要发回客户端的消息列表。
"""

from __future__ import annotations

from typing import Any

from ..components import ui as ui_module
from ..components.ui import UIComponent
from ..core import (
    Cell,
    CellGraph,
    CellStatus,
    Executor,
    analyze_cell,
    create_cell,
)
from .protocol import (
    make_cell_result_message,
    make_error_message,
    make_graph_changed_message,
    make_state_message,
)


class NotebookSession:
    def __init__(self) -> None:
        self._graph = CellGraph()
        self._executor = Executor(self._graph)
        self._executor.inject("ui", ui_module)
        self._cell_counter = 0

    @property
    def graph(self) -> CellGraph:
        return self._graph

    def handle_message(self, msg: dict[str, Any]) -> list[dict[str, Any]]:
        msg_type = msg.get("type")
        handler = {
            "get_state": self._handle_get_state,
            "update_cell": self._handle_update_cell,
            "run_cell": self._handle_run_cell,
            "run_all": self._handle_run_all,
            "add_cell": self._handle_add_cell,
            "remove_cell": self._handle_remove_cell,
            "ui_event": self._handle_ui_event,
        }.get(msg_type)

        if handler is None:
            return [make_error_message(f"未知消息类型: {msg_type}")]
        try:
            return handler(msg)
        except Exception as e:
            return [make_error_message(f"{type(e).__name__}: {e}")]

    def _update_component_ids(self) -> None:
        for cell_id in self._graph.cell_ids:
            cell = self._graph.get_cell(cell_id)
            for var_name, value in cell.namespace.items():
                if isinstance(value, UIComponent):
                    value.component_id = f"{cell_id}:{var_name}"

    def _handle_get_state(self, msg: dict) -> list[dict]:
        self._update_component_ids()
        return [make_state_message(self._graph)]

    def _handle_update_cell(self, msg: dict) -> list[dict]:
        cell_id = msg["cell_id"]
        new_code = msg["code"]
        defs, refs = analyze_cell(new_code)
        new_cell = Cell(cell_id=cell_id, code=new_code, defs=defs, refs=refs)
        self._graph.remove_cell(cell_id)
        self._graph.add_cell(new_cell)
        return [make_graph_changed_message(self._graph)]

    def _handle_run_cell(self, msg: dict) -> list[dict]:
        cell_id = msg["cell_id"]
        self._executor.run_cell(cell_id)
        self._update_component_ids()
        return self._collect_results()

    def _handle_run_all(self, msg: dict) -> list[dict]:
        self._executor.run_all()
        self._update_component_ids()
        return self._collect_results()

    def _handle_add_cell(self, msg: dict) -> list[dict]:
        code = msg.get("code", "")
        cell_id = f"cell_{self._cell_counter}"
        self._cell_counter += 1
        self._graph.add_cell(create_cell(cell_id, code))
        return [make_graph_changed_message(self._graph)]

    def _handle_remove_cell(self, msg: dict) -> list[dict]:
        cell_id = msg["cell_id"]
        self._graph.remove_cell(cell_id)
        return [make_graph_changed_message(self._graph)]

    def _handle_ui_event(self, msg: dict) -> list[dict]:
        component_id = msg["component_id"]
        new_value = msg["value"]

        parts = component_id.split(":", 1)
        if len(parts) != 2:
            return [make_error_message(f"无效的组件 ID: {component_id}")]
        cell_id, var_name = parts

        cell = self._graph.get_cell(cell_id)
        component = cell.namespace.get(var_name)

        if not isinstance(component, UIComponent):
            return [make_error_message(f"组件 {component_id} 未找到")]

        component.set_value(new_value)
        self._executor.run_descendants(cell_id)
        self._update_component_ids()
        return self._collect_results()

    def _collect_results(self) -> list[dict]:
        results: list[dict] = []
        for cid in self._graph.topological_order():
            cell = self._graph.get_cell(cid)
            results.append(make_cell_result_message(cell))
        return results
