"""测试解析：.py 文本 → CellGraph。"""

from __future__ import annotations

import pytest

from backend.storage.parser import ParseError, py_to_graph


SIMPLE_NOTEBOOK = """\
import marimo_from_scratch as marimo

app = marimo.App()

@app.cell
def _():
    x = 10
    return (x,)

@app.cell
def _(x):
    y = x + 5
    return (y,)
"""


def test_parse_simple():
    graph = py_to_graph(SIMPLE_NOTEBOOK)
    assert len(graph.cell_ids) == 2
    cell0 = graph.get_cell("cell_0")
    assert cell0.defs == {"x"}
    assert cell0.refs == set()
    cell1 = graph.get_cell("cell_1")
    assert cell1.defs == {"y"}
    assert cell1.refs == {"x"}


def test_parse_extracts_code():
    graph = py_to_graph(SIMPLE_NOTEBOOK)
    cell0 = graph.get_cell("cell_0")
    assert "x = 10" in cell0.code
    cell1 = graph.get_cell("cell_1")
    assert "y = x + 5" in cell1.code


def test_parse_multiple_defs():
    source = """\
import marimo_from_scratch as marimo

app = marimo.App()

@app.cell
def _():
    x = 1
    y = 2
    return (x, y)
"""
    graph = py_to_graph(source)
    cell = graph.get_cell("cell_0")
    assert cell.defs == {"x", "y"}


def test_parse_no_cells():
    source = """\
import marimo_from_scratch as marimo

app = marimo.App()
"""
    graph = py_to_graph(source)
    assert len(graph.cell_ids) == 0


def test_parse_syntax_error():
    with pytest.raises(ParseError):
        py_to_graph("def :(")


def test_parse_preserves_dependency():
    source = """\
import marimo_from_scratch as marimo

app = marimo.App()

@app.cell
def _():
    n = 5
    return (n,)

@app.cell
def _(n):
    s = n * n
    return (s,)

@app.cell
def _(s):
    r = s + 1
    return (r,)
"""
    graph = py_to_graph(source)
    assert graph.predecessors("cell_1") == {"cell_0"}
    assert graph.predecessors("cell_2") == {"cell_1"}
    assert graph.descendants("cell_0") == {"cell_1", "cell_2"}