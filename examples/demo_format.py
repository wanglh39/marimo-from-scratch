"""M2 demo：.py notebook 文件格式 —— 序列化、解析、直接运行。

运行方式：uv run python -m examples.demo_format
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from backend.core import CellGraph, Executor, create_cell
from backend.storage.parser import py_to_graph
from backend.storage.serializer import graph_to_py


def main() -> None:
    print("=" * 60)
    print("  M2 文件格式 demo：.py ⇄ notebook 双向转换")
    print("=" * 60)

    graph = CellGraph()
    graph.add_cell(create_cell("base", "n = 5"))
    graph.add_cell(create_cell("square", "s = n * n"))
    graph.add_cell(create_cell("report", "print(f'n={n}, s={s}')\ns + 1"))

    print("\n【1. 原始 notebook 的 cell 和依赖关系】\n")
    for cid in graph.topological_order():
        cell = graph.get_cell(cid)
        print(f"  {cid:12s}  defs={cell.defs}  refs={cell.refs}  code: {cell.code}")

    print("\n【2. 序列化为 .py 文件】\n")
    py_text = graph_to_py(graph)
    print(py_text)

    print("【3. 从 .py 文本解析回 CellGraph】\n")
    graph2 = py_to_graph(py_text)
    for cid in graph2.topological_order():
        cell = graph2.get_cell(cid)
        print(f"  {cid:12s}  defs={cell.defs}  refs={cell.refs}  code: {cell.code!r}")

    print("\n【4. 解析后执行，验证结果一致】\n")
    ex1 = Executor(graph)
    ex2 = Executor(graph2)
    ex1.run_all()
    ex2.run_all()
    print(f"  原始: n={ex1.global_namespace['n']}, s={ex1.global_namespace['s']}")
    print(f"  解析: n={ex2.global_namespace['n']}, s={ex2.global_namespace['s']}")

    print("\n【5. 直接 `python notebook.py` 运行（App.run）】\n")
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(py_text)
        tmp_path = f.name

    project_root = str(Path(__file__).resolve().parent.parent)
    import os
    run_env = {**os.environ, "PYTHONPATH": project_root}
    result = subprocess.run(
        [sys.executable, tmp_path],
        capture_output=True,
        text=True,
        env=run_env,
    )
    print(result.stdout)
    if result.stderr:
        print(f"  stderr: {result.stderr.strip()}")

    Path(tmp_path).unlink()

    print("=" * 60)
    print("  demo 结束。核心要点：")
    print("  1. notebook 可序列化为合法的 .py 文件")
    print("  2. .py 文件可解析回 notebook（双向转换）")
    print("  3. .py 文件可直接 python 运行（App.run）")
    print("=" * 60)


if __name__ == "__main__":
    main()