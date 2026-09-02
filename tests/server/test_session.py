"""测试 NotebookSession：WebSocket 会话的消息处理。"""

from __future__ import annotations

from backend.server.session import NotebookSession


def send(session: NotebookSession, msg: dict) -> list[dict]:
    return session.handle_message(msg)


def test_get_state_empty():
    session = NotebookSession()
    resp = send(session, {"type": "get_state"})
    assert resp[0]["type"] == "state"
    assert resp[0]["cells"] == []
    assert resp[0]["edges"] == []


def test_add_cell():
    session = NotebookSession()
    resp = send(session, {"type": "add_cell", "code": "x = 1"})
    assert resp[0]["type"] == "graph_changed"
    assert len(resp[0]["cells"]) == 1
    assert resp[0]["cells"][0]["code"] == "x = 1"
    assert resp[0]["cells"][0]["defs"] == ["x"]


def test_run_cell():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "x = 10"})
    send(session, {"type": "add_cell", "code": "y = x + 5"})
    resp = send(session, {"type": "run_all"})
    assert len(resp) == 2
    assert resp[0]["cell_id"] == "cell_0"
    assert resp[0]["status"] == "done"
    assert resp[0]["output"] is None
    assert resp[1]["cell_id"] == "cell_1"
    assert resp[1]["status"] == "done"


def test_run_all_with_output():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "x = 5\nx * 2"})
    resp = send(session, {"type": "run_all"})
    assert resp[0]["output"] == 10


def test_reactive_update():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "n = 5"})
    send(session, {"type": "add_cell", "code": "s = n * n"})
    send(session, {"type": "run_all"})

    send(session, {"type": "update_cell", "cell_id": "cell_0", "code": "n = 10"})
    resp = send(session, {"type": "run_cell", "cell_id": "cell_0"})

    cell_results = {r["cell_id"]: r for r in resp if r["type"] == "cell_result"}
    assert len(cell_results) == 2
    assert cell_results["cell_0"]["status"] == "done"
    assert cell_results["cell_1"]["status"] == "done"


def test_short_circuit():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "x = 1 / 0"})
    send(session, {"type": "add_cell", "code": "y = x + 1"})
    resp = send(session, {"type": "run_all"})

    assert resp[0]["status"] == "error"
    assert resp[0]["exception_type"] == "ZeroDivisionError"
    assert resp[1]["status"] == "stale"


def test_remove_cell():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "x = 1"})
    send(session, {"type": "add_cell", "code": "y = x + 1"})
    resp = send(session, {"type": "remove_cell", "cell_id": "cell_1"})
    assert resp[0]["type"] == "graph_changed"
    assert len(resp[0]["cells"]) == 1


def test_unknown_message_type():
    session = NotebookSession()
    resp = send(session, {"type": "unknown"})
    assert resp[0]["type"] == "error"


def test_stdout_capture():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "print('hello')"})
    resp = send(session, {"type": "run_all"})
    assert resp[0]["stdout"] == "hello\n"


def test_graph_changed_on_update():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "x = 1"})
    resp = send(session, {"type": "update_cell", "cell_id": "cell_0", "code": "x = 1\ny = 2"})
    assert resp[0]["type"] == "graph_changed"
    cell = resp[0]["cells"][0]
    assert cell["defs"] == ["x", "y"]


def test_output_serialization():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "x = [1, 2, 3]\nx"})
    resp = send(session, {"type": "run_all"})
    assert resp[0]["output"] == [1, 2, 3]

    send(session, {"type": "update_cell", "cell_id": "cell_0", "code": "x = {1, 2, 3}\nx"})
    resp = send(session, {"type": "run_all"})
    assert isinstance(resp[0]["output"], str)
    assert "1" in resp[0]["output"]