"""测试序列化：CellGraph → .py 文本。"""

from __future__ import annotations

from backend.core import CellGraph, create_cell
from backend.storage.serializer import graph_to_py


def build(*cells):
    g = CellGraph()
    for c in cells:
        g.add_cell(c)
    return g


def test_simple_serialize():
    g = build(create_cell("a", "x = 10"), create_cell("b", "y = x + 5"))
    result = graph_to_py(g)
    assert "from backend.app import App" in result
    assert "app = App()" in result
    assert "@app.cell" in result
    assert "def _():" in result
    assert "def _(x):" in result
    assert "return (x,)" in result
    assert "return (y,)" in result
    assert 'if __name__ == "__main__":' in result


def test_serialize_preserves_code():
    g = build(create_cell("a", "x = 1\ny = 2"))
    result = graph_to_py(g)
    assert "x = 1" in result
    assert "y = 2" in result
    assert "return (x, y)" in result


def test_serialize_no_defs():
    g = build(create_cell("a", "print('hello')"))
    result = graph_to_py(g)
    assert "return" in result
    assert "return ()" not in result


def test_serialize_empty_code():
    g = build(create_cell("a", ""))
    result = graph_to_py(g)
    assert "@app.cell" in result
    assert "return" in result