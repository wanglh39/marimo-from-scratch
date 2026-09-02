"""测试 UI 组件系统：slider/button reactive binding。"""

from __future__ import annotations

from backend.server.session import NotebookSession


def send(session: NotebookSession, msg: dict) -> list[dict]:
    return session.handle_message(msg)


def test_slider_creation():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "s = ui.slider(0, 100, value=50)"})
    resp = send(session, {"type": "run_all"})
    comps = resp[0]["components"]
    assert len(comps) == 1
    assert comps[0]["type"] == "slider"
    assert comps[0]["value"] == 50
    assert comps[0]["props"]["min"] == 0
    assert comps[0]["props"]["max"] == 100


def test_component_id_set():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "s = ui.slider(value=50)"})
    resp = send(session, {"type": "run_all"})
    assert resp[0]["components"][0]["id"] == "cell_0:s"


def test_ui_event_reactive():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "s = ui.slider(0, 100, value=50)"})
    send(session, {"type": "add_cell", "code": "s.value * 2"})
    send(session, {"type": "run_all"})

    results = {r["cell_id"]: r for r in send(session, {"type": "run_all"})}
    assert results["cell_1"]["output"] == 100

    resp = send(session, {"type": "ui_event", "component_id": "cell_0:s", "value": 80})
    results = {r["cell_id"]: r for r in resp}
    assert results["cell_1"]["output"] == 160


def test_ui_event_updates_component_value():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "s = ui.slider(0, 100, value=50)"})
    send(session, {"type": "run_all"})

    send(session, {"type": "ui_event", "component_id": "cell_0:s", "value": 75})
    resp = send(session, {"type": "get_state"})
    comp = resp[0]["cells"][0]["components"][0]
    assert comp["value"] == 75


def test_button_component():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "b = ui.button('Click me')"})
    resp = send(session, {"type": "run_all"})
    comp = resp[0]["components"][0]
    assert comp["type"] == "button"
    assert comp["props"]["label"] == "Click me"
    assert comp["value"] == 0


def test_button_click_reactive():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "b = ui.button('Click')"})
    send(session, {"type": "add_cell", "code": "f'clicked {b.value} times'"})
    send(session, {"type": "run_all"})

    results = {r["cell_id"]: r for r in send(session, {"type": "run_all"})}
    assert results["cell_1"]["output"] == "clicked 0 times"

    send(session, {"type": "ui_event", "component_id": "cell_0:b", "value": 3})
    resp = send(session, {"type": "get_state"})
    assert resp[0]["cells"][1]["output"] == "clicked 3 times"


def test_checkbox_component():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "c = ui.checkbox('Enable', value=False)"})
    send(session, {"type": "add_cell", "code": "'ON' if c.value else 'OFF'"})
    send(session, {"type": "run_all"})

    results = {r["cell_id"]: r for r in send(session, {"type": "run_all"})}
    assert results["cell_1"]["output"] == "OFF"

    send(session, {"type": "ui_event", "component_id": "cell_0:c", "value": True})
    resp = send(session, {"type": "get_state"})
    assert resp[0]["cells"][1]["output"] == "ON"


def test_ui_event_invalid_component():
    session = NotebookSession()
    resp = send(session, {"type": "ui_event", "component_id": "cell_0:s", "value": 1})
    assert resp[0]["type"] == "error"


def test_slider_in_output():
    session = NotebookSession()
    send(session, {"type": "add_cell", "code": "ui.slider(0, 10, value=5)"})
    resp = send(session, {"type": "run_all"})
    assert resp[0]["output"]["_ui"] is True
    assert resp[0]["output"]["type"] == "slider"
    assert resp[0]["output"]["value"] == 5