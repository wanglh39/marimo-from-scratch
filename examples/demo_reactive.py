"""M1 demo：直观感受 reactive 执行引擎。

运行方式：uv run python examples/demo_reactive.py
"""

from __future__ import annotations

from backend.core import CellStatus, CellGraph, Executor, create_cell


def print_status(graph: CellGraph, executor: Executor) -> None:
    print("-" * 60)
    for cid in graph.topological_order():
        cell = graph.get_cell(cid)
        status_icon = {
            CellStatus.DONE: "✓",
            CellStatus.ERROR: "✗",
            CellStatus.STALE: "○",
            CellStatus.IDLE: "·",
            CellStatus.RUNNING: "→",
            CellStatus.PENDING: "…",
        }[cell.status]
        ns_preview = ", ".join(f"{k}={v}" for k, v in cell.namespace.items())
        print(f"  [{status_icon}] {cid:12s}  code: {cell.code:30s}  → {ns_preview}")
        if cell.exception:
            print(f"      ⚠ {type(cell.exception).__name__}: {cell.exception}")
        if cell.stdout:
            print(f"      stdout: {cell.stdout.strip()}")
        if cell.output is not None:
            print(f"      output: {cell.output!r}")
    print("-" * 60)


def main() -> None:
    print("=" * 60)
    print("  marimo-from-scratch · M1 reactive 执行引擎 demo")
    print("=" * 60)

    graph = CellGraph()
    graph.add_cell(create_cell("base", "n = 5"))
    graph.add_cell(create_cell("square", "s = n * n"))
    graph.add_cell(create_cell("report", "print(f'n={n}, s={s}')\ns + 1"))

    executor = Executor(graph)

    print("\n【第一次执行】全量执行所有 cell：\n")
    executor.run_all()
    print_status(graph, executor)

    print("\n【reactive 更新】把 base 的 n 从 5 改成 10，只重跑受影响的 cell：\n")
    graph.remove_cell("base")
    graph.add_cell(create_cell("base", "n = 10"))
    executed = executor.run_cell("base")
    print(f"  实际执行的 cell: {executed}")
    print_status(graph, executor)

    print("\n【短路机制】把 base 改成会出错的代码，下游应被标记 STALE：\n")
    graph.remove_cell("base")
    graph.add_cell(create_cell("base", "n = 1 / 0"))
    executed = executor.run_cell("base")
    print(f"  实际执行的 cell: {executed}")
    print_status(graph, executor)

    print("\n【恢复】修复 base，下游应自动恢复执行：\n")
    graph.remove_cell("base")
    graph.add_cell(create_cell("base", "n = 3"))
    executed = executor.run_cell("base")
    print(f"  实际执行的 cell: {executed}")
    print_status(graph, executor)

    print("\n【增量跳过】改一个无人依赖的独立 cell，其他 cell 不受影响：\n")
    graph.add_cell(create_cell("isolated", "msg = 'hello'"))
    executor.run_all()
    graph.remove_cell("isolated")
    graph.add_cell(create_cell("isolated", "msg = 'world'"))
    executed = executor.run_cell("isolated")
    print(f"  实际执行的 cell: {executed}")
    print_status(graph, executor)

    print("\n" + "=" * 60)
    print("  demo 结束。核心要点：")
    print("  1. 改一个 cell → 只有它和后代重跑（增量执行）")
    print("  2. cell 出错 → 后代标记 STALE 不执行（短路）")
    print("  3. 修复错误 → 后代自动恢复（reactive）")
    print("=" * 60)


if __name__ == "__main__":
    main()