"""往返测试：graph → py → graph 语义等价。"""

from __future__ import annotations

import ast

from backend.core import CellGraph, Executor, create_cell
from backend.storage.parser import py_to_graph
from backend.storage.serializer import graph_to_py


def build(*cells):
    g = CellGraph()
    for c in cells:
        g.add_cell(c)
    return g


def assert_graphs_equivalent(g1: CellGraph, g2: CellGraph) -> None:
    order1 = g1.topological_order()
    order2 = g2.topological_order()
    assert len(order1) == len(order2), "cell 数量不同"

    for cid1, cid2 in zip(order1, order2):
        c1 = g1.get_cell(cid1)
        c2 = g2.get_cell(cid2)
        assert c1.defs == c2.defs, f"defs 不同: {c1.defs} vs {c2.defs}"
        assert c1.refs == c2.refs, f"refs 不同: {c1.refs} vs {c2.refs}"
        dump1 = ast.dump(ast.parse(c1.code)) if c1.code.strip() else ""
        dump2 = ast.dump(ast.parse(c2.code)) if c2.code.strip() else ""
        assert dump1 == dump2, f"code 语义不同:\n{c1.code}\nvs\n{c2.code}"


def assert_execution_equivalent(g1: CellGraph, g2: CellGraph) -> None:
    ex1 = Executor(g1)
    ex2 = Executor(g2)
    ex1.run_all()
    ex2.run_all()
    ns1 = ex1.global_namespace
    ns2 = ex2.global_namespace
    assert set(ns1.keys()) == set(ns2.keys()), (
        f"命名空间键不同: {set(ns1.keys())} vs {set(ns2.keys())}"
    )
    for key in ns1:
        v1, v2 = ns1[key], ns2[key]
        if callable(v1) or callable(v2):
            continue
        assert v1 == v2, (
            f"变量 {key} 值不同: {v1} vs {v2}"
        )


def test_roundtrip_simple():
    g = build(create_cell("a", "x = 10"), create_cell("b", "y = x + 5"))
    py_text = graph_to_py(g)
    g2 = py_to_graph(py_text)
    assert_graphs_equivalent(g, g2)
    assert_execution_equivalent(g, g2)


def test_roundtrip_chain():
    g = build(
        create_cell("a", "n = 5"),
        create_cell("b", "s = n * n"),
        create_cell("c", "r = s + 1"),
    )
    py_text = graph_to_py(g)
    g2 = py_to_graph(py_text)
    assert_graphs_equivalent(g, g2)
    assert_execution_equivalent(g, g2)


def test_roundtrip_diamond():
    g = build(
        create_cell("a", "x = 10"),
        create_cell("b", "y = x + 1"),
        create_cell("c", "z = x * 2"),
        create_cell("d", "w = y + z"),
    )
    py_text = graph_to_py(g)
    g2 = py_to_graph(py_text)
    assert_graphs_equivalent(g, g2)
    assert_execution_equivalent(g, g2)


def test_roundtrip_with_function():
    g = build(
        create_cell("f", "def double(v):\n    return v * 2"),
        create_cell("d", "n = 5"),
        create_cell("u", "result = double(n)"),
    )
    py_text = graph_to_py(g)
    g2 = py_to_graph(py_text)
    assert_graphs_equivalent(g, g2)
    assert_execution_equivalent(g, g2)


def test_roundtrip_with_import():
    g = build(
        create_cell("a", "import math"),
        create_cell("b", "v = math.pi"),
    )
    py_text = graph_to_py(g)
    g2 = py_to_graph(py_text)
    assert_graphs_equivalent(g, g2)
    assert_execution_equivalent(g, g2)


def test_roundtrip_multiple_defs():
    g = build(create_cell("a", "x = 1\ny = 2\nz = 3"))
    py_text = graph_to_py(g)
    g2 = py_to_graph(py_text)
    assert_graphs_equivalent(g, g2)
    assert_execution_equivalent(g, g2)


def test_double_roundtrip_stable():
    g = build(create_cell("a", "x = 1"), create_cell("b", "y = x + 1"))
    py1 = graph_to_py(g)
    g2 = py_to_graph(py1)
    py2 = graph_to_py(g2)
    g3 = py_to_graph(py2)
    assert_graphs_equivalent(g2, g3)