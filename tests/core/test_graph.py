"""测试 DAG 构建：依赖关系、拓扑排序、环检测、增量执行顺序。"""

from __future__ import annotations

import pytest

from backend.core import CellGraph, CyclicDependencyError, DuplicateDefinitionError, create_cell


def build_graph(*cells):
    g = CellGraph()
    for c in cells:
        g.add_cell(c)
    return g


def test_simple_dependency():
    g = build_graph(
        create_cell("a", "x = 1"),
        create_cell("b", "y = x + 1"),
    )
    assert g.predecessors("b") == {"a"}
    assert g.successors("a") == {"b"}
    assert g.descendants("a") == {"b"}
    assert g.ancestors("b") == {"a"}


def test_no_dependency():
    g = build_graph(
        create_cell("a", "x = 1"),
        create_cell("b", "y = 2"),
    )
    assert g.predecessors("a") == set()
    assert g.predecessors("b") == set()
    assert g.descendants("a") == set()


def test_chain_dependency():
    g = build_graph(
        create_cell("a", "x = 1"),
        create_cell("b", "y = x + 1"),
        create_cell("c", "z = y * 2"),
    )
    assert g.descendants("a") == {"b", "c"}
    assert g.ancestors("c") == {"a", "b"}
    order = g.topological_order()
    assert order.index("a") < order.index("b") < order.index("c")


def test_diamond_dependency():
    g = build_graph(
        create_cell("a", "x = 1"),
        create_cell("b", "y = x + 1"),
        create_cell("c", "z = x * 2"),
        create_cell("d", "w = y + z"),
    )
    order = g.topological_order()
    assert order.index("a") < order.index("b")
    assert order.index("a") < order.index("c")
    assert order.index("b") < order.index("d")
    assert order.index("c") < order.index("d")
    assert g.descendants("a") == {"b", "c", "d"}


def test_duplicate_definition():
    with pytest.raises(DuplicateDefinitionError):
        build_graph(
            create_cell("a", "x = 1"),
            create_cell("b", "x = 2"),
        )


def test_cyclic_dependency():
    with pytest.raises(CyclicDependencyError):
        g = build_graph(
            create_cell("a", "y = x + 1"),
            create_cell("b", "x = y + 1"),
        )
        g.topological_order()


def test_execution_order_from():
    g = build_graph(
        create_cell("a", "x = 1"),
        create_cell("b", "y = x + 1"),
        create_cell("c", "z = y * 2"),
        create_cell("d", "w = 100"),
    )
    order = g.execution_order_from("b")
    assert set(order) == {"b", "c"}
    assert order.index("b") < order.index("c")
    assert "a" not in order
    assert "d" not in order


def test_remove_cell():
    g = build_graph(
        create_cell("a", "x = 1"),
        create_cell("b", "y = x + 1"),
    )
    g.remove_cell("b")
    assert "b" not in g.cell_ids
    assert g.successors("a") == set()