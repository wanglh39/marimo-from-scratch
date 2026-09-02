"""序列化：CellGraph → .py 文件文本。

按拓扑顺序输出每个 cell 为一个被 @app.cell 装饰的函数。
"""

from __future__ import annotations

from ..core import CellGraph

_HEADER = """\
from backend.app import App

app = App()
"""


def graph_to_py(graph: CellGraph) -> str:
    lines: list[str] = [_HEADER]

    for cell_id in graph.topological_order():
        cell = graph.get_cell(cell_id)
        refs_str = ", ".join(sorted(cell.refs))
        defs_list = sorted(cell.defs)

        lines.append("@app.cell")
        lines.append(f"def _({refs_str}):")

        if cell.code.strip():
            for code_line in cell.code.splitlines():
                lines.append(f"    {code_line}")

        if defs_list:
            defs_str = ", ".join(defs_list)
            if len(defs_list) == 1:
                lines.append(f"    return ({defs_str},)")
            else:
                lines.append(f"    return ({defs_str})")
        else:
            lines.append("    return")

        lines.append("")

    lines.append('if __name__ == "__main__":')
    lines.append("    app.run()")
    lines.append("")

    return "\n".join(lines)