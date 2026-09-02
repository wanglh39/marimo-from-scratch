"""WebSocket 消息协议：序列化 cell 状态、构造响应消息。

消息流向：
  客户端 → 服务端：get_state / update_cell / run_cell / run_all / add_cell / remove_cell
  服务端 → 客户端：state / cell_result / graph_changed / error
"""

from __future__ import annotations

import json
from typing import Any

from ..components.ui import UIComponent
from ..core import Cell, CellGraph


def _is_ui_component(obj: Any) -> bool:
    return isinstance(obj, UIComponent)


def serialize_output(output: Any) -> Any:
    if output is None:
        return None
    if _is_ui_component(output):
        return output.to_dict()
    try:
        json.dumps(output)
        return output
    except (TypeError, ValueError):
        return repr(output)


def _extract_components(cell: Cell) -> list[dict[str, Any]]:
    components: list[dict[str, Any]] = []
    for var_name, value in cell.namespace.items():
        if _is_ui_component(value):
            comp_dict = value.to_dict()
            comp_dict["var_name"] = var_name
            components.append(comp_dict)
    return components


def make_cell_info(cell: Cell) -> dict[str, Any]:
    return {
        "cell_id": cell.cell_id,
        "code": cell.code,
        "defs": sorted(cell.defs),
        "refs": sorted(cell.refs),
        "status": cell.status.value,
        "output": serialize_output(cell.output),
        "stdout": cell.stdout,
        "exception": repr(cell.exception) if cell.exception else None,
        "exception_type": type(cell.exception).__name__ if cell.exception else None,
        "components": _extract_components(cell),
    }


def make_state_message(graph: CellGraph) -> dict[str, Any]:
    cells = [
        make_cell_info(graph.get_cell(cid)) for cid in graph.topological_order()
    ]
    edges: list[list[str]] = []
    for cid in graph.cell_ids:
        for succ in sorted(graph.successors(cid)):
            edges.append([cid, succ])
    return {"type": "state", "cells": cells, "edges": edges}


def make_cell_result_message(cell: Cell) -> dict[str, Any]:
    return {
        "type": "cell_result",
        "cell_id": cell.cell_id,
        "status": cell.status.value,
        "output": serialize_output(cell.output),
        "stdout": cell.stdout,
        "exception": repr(cell.exception) if cell.exception else None,
        "exception_type": type(cell.exception).__name__ if cell.exception else None,
        "components": _extract_components(cell),
    }


def make_graph_changed_message(graph: CellGraph) -> dict[str, Any]:
    cells = [
        make_cell_info(graph.get_cell(cid)) for cid in graph.topological_order()
    ]
    edges: list[list[str]] = []
    for cid in graph.cell_ids:
        for succ in sorted(graph.successors(cid)):
            edges.append([cid, succ])
    return {"type": "graph_changed", "cells": cells, "edges": edges}


def make_error_message(message: str) -> dict[str, Any]:
    return {"type": "error", "message": message}