"""storage: .py notebook 文件格式 —— 序列化与解析。

格式设计（教学版）：
  - 每个 cell 是一个被 @app.cell 装饰的函数
  - 函数参数 = cell 引用的变量（refs），按字母序排列
  - return 语句 = cell 定义的变量（defs），以 tuple 形式
  - 函数体 = cell 的实际代码
  - 整个 .py 文件是合法 Python，可直接 `python notebook.py` 运行
"""