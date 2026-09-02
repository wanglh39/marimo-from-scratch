"""示例 notebook：展示 marimo-from-scratch 的完整功能。

运行方式：uv-uv run python -m examples.demo_notebook
"""

from backend.app import App

app = App()


@app.cell
def _():
    n = 10
    return (n,)


@app.cell
def _(n):
    def factorial(x):
        if x <= 1:
            return 1
        return x * factorial(x - 1)

    return (factorial,)


@app.cell
def _(factorial, n):
    result = factorial(n)
    return (result,)


@app.cell
def _(result):
    print(f"factorial({10}) = {result}")
    result
    return


@app.cell
def _():
    s = ui.slider(1, 20, value=5)
    return (s,)


@app.cell
def _(s):
    print(f"slider value = {s.value}")
    s.value ** 2
    return


if __name__ == "__main__":
    app.run()