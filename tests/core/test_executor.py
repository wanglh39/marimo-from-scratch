"""测试执行引擎：全量执行、增量执行、短路、output/stdout 捕获。"""

from __future__ import annotations

from backend.core import CellGraph, CellStatus, Executor, create_cell


def build_graph(*codes: tuple[str, str]) -> CellGraph:
    g = CellGraph()
    for cid, code in codes:
        g.add_cell(create_cell(cid, code))
    return g


def test_run_all_basic():
    g = build_graph(("a", "x = 10"), ("b", "y = x + 5"), ("c", "z = y * 2"))
    ex = Executor(g)
    ex.run_all()
    assert ex.global_namespace["x"] == 10
    assert ex.global_namespace["y"] == 15
    assert ex.global_namespace["z"] == 30
    assert all(
        g.get_cell(cid).status is CellStatus.DONE for cid in ("a", "b", "c")
    )


def test_output_extraction():
    g = build_graph(("a", "x = 1\nx + 2"))
    ex = Executor(g)
    ex.run_all()
    assert g.get_cell("a").output == 3


def test_output_none_for_assignment():
    g = build_graph(("a", "x = 1"))
    ex = Executor(g)
    ex.run_all()
    assert g.get_cell("a").output is None


def test_stdout_capture():
    g = build_graph(("a", 'print("hello")'))
    ex = Executor(g)
    ex.run_all()
    assert g.get_cell("a").stdout == "hello\n"


def test_namespace_isolation():
    g = build_graph(("a", "x = 1\ny = 2"), ("b", "z = x + y"))
    ex = Executor(g)
    ex.run_all()
    assert g.get_cell("a").namespace == {"x": 1, "y": 2}
    assert g.get_cell("b").namespace == {"z": 3}


def test_reactive_update():
    g = build_graph(("base", "n = 5"), ("square", "s = n * n"), ("report", "r = s + 1"))
    ex = Executor(g)
    ex.run_all()
    assert ex.global_namespace["s"] == 25
    assert ex.global_namespace["r"] == 26

    g.remove_cell("base")
    g.add_cell(create_cell("base", "n = 10"))
    executed = ex.run_cell("base")

    assert set(executed) == {"base", "square", "report"}
    assert ex.global_namespace["n"] == 10
    assert ex.global_namespace["s"] == 100
    assert ex.global_namespace["r"] == 101


def test_incremental_skips_unaffected():
    g = build_graph(
        ("a", "x = 1"),
        ("b", "y = x + 1"),
        ("c", "z = 999"),
    )
    ex = Executor(g)
    ex.run_all()

    g.remove_cell("c")
    g.add_cell(create_cell("c", "z = 1000"))
    executed = ex.run_cell("c")

    assert executed == ["c"]
    assert ex.global_namespace["z"] == 1000
    assert ex.global_namespace["y"] == 2


def test_short_circuit_on_error():
    g = build_graph(
        ("a", "x = 1 / 0"),
        ("b", "y = x + 1"),
        ("c", "z = y * 2"),
    )
    ex = Executor(g)
    ex.run_all()
    assert g.get_cell("a").status is CellStatus.ERROR
    assert g.get_cell("b").status is CellStatus.STALE
    assert g.get_cell("c").status is CellStatus.STALE
    assert isinstance(g.get_cell("a").exception, ZeroDivisionError)


def test_exception_capture():
    g = build_graph(("a", "x = int('abc')"))
    ex = Executor(g)
    ex.run_all()
    assert g.get_cell("a").status is CellStatus.ERROR
    assert isinstance(g.get_cell("a").exception, ValueError)


def test_diamond_execution():
    g = build_graph(
        ("a", "x = 10"),
        ("b", "y = x + 1"),
        ("c", "z = x * 2"),
        ("d", "w = y + z"),
    )
    ex = Executor(g)
    ex.run_all()
    assert ex.global_namespace["y"] == 11
    assert ex.global_namespace["z"] == 20
    assert ex.global_namespace["w"] == 31


def test_reactive_chain_with_function():
    g = build_graph(
        ("def_cell", "def double(v):\n    return v * 2"),
        ("data", "n = 5"),
        ("use", "result = double(n)"),
    )
    ex = Executor(g)
    ex.run_all()
    assert ex.global_namespace["result"] == 10

    g.remove_cell("data")
    g.add_cell(create_cell("data", "n = 50"))
    ex.run_cell("data")
    assert ex.global_namespace["result"] == 100


def test_stale_upstream_blocks_execution():
    g = build_graph(
        ("a", "x = 1 / 0"),
        ("b", "y = x + 1"),
    )
    ex = Executor(g)
    ex.run_all()
    assert g.get_cell("b").status is CellStatus.STALE

    g.remove_cell("a")
    g.add_cell(create_cell("a", "x = 42"))
    ex.run_cell("a")
    assert g.get_cell("a").status is CellStatus.DONE
    assert g.get_cell("b").status is CellStatus.DONE
    assert ex.global_namespace["y"] == 43