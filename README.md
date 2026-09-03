# marimo-from-scratch

从零实现 [marimo](https://github.com/marimo-team/marimo)：理解 reactive Python notebook 的底层原理与设计哲学。

## 这是什么？

一个教学项目，用约 5000 行代码复刻 marimo 的核心功能，配套 46 章详尽文档（约 20 万字），部署在 GitHub Pages。

**📖 在线文档**：https://wanglh39.github.io/marimo-from-scratch/

## 核心原理

marimo 是一个 **reactive Python notebook**——像电子表格一样，改一个 cell，依赖它的 cell 自动更新。

| Jupyter 的问题 | marimo 的解法 |
|---|---|
| 隐藏状态（乱序执行） | **Reactivity**：DAG 驱动，改一个 cell → 后代自动更新 |
| `.ipynb` 笨重 JSON | **Pure Python**：`.py` 文件即 notebook，也是可部署的 app |
| 执行顺序 = cell 排列 | **DAG**：执行顺序由变量依赖关系静态确定 |

**核心机制**：AST 静态分析提取每个 cell 的 defs/refs → 构建 DAG → 拓扑排序 + 增量执行 + 短路。

## 快速开始

### 后端

```bash
uv sync                                    # 安装依赖
uv run pytest                              # 运行测试 (79个)
uv run python -m examples.demo_reactive    # reactive demo
uv run python -m examples.demo_format      # 文件格式 demo
uv run python -m examples.demo_notebook    # 示例 notebook
```

### 前端 + 后端（浏览器 notebook）

```bash
# 终端 1 - 后端
uv run uvicorn backend.server.webapp:app --reload --port 8000

# 终端 2 - 前端
cd frontend && npm install && npm run dev

# 浏览器打开 http://localhost:5173
```

### 文档站

**在线阅读**：https://wanglh39.github.io/marimo-from-scratch/

本地预览：

```bash
cd docs && npm install && npm run dev
```

## 文档目录

| 篇 | 章节 | 链接 |
|---|---|---|
| 第一篇：背景与动机 | ch01-05 | [目录](https://wanglh39.github.io/marimo-from-scratch/overview/ch01) |
| 第二篇：Cell 与 AST 分析 | ch06-11 | [目录](https://wanglh39.github.io/marimo-from-scratch/cell-ast/ch06) |
| 第三篇：DAG 构建 | ch12-16 | [目录](https://wanglh39.github.io/marimo-from-scratch/dag/ch12) |
| 第四篇：执行引擎 | ch17-22 | [目录](https://wanglh39.github.io/marimo-from-scratch/execution/ch17) |
| 第五篇：文件格式 | ch23-27 | [目录](https://wanglh39.github.io/marimo-from-scratch/file-format/ch23) |
| 第六篇：通信协议 | ch28-31 | [目录](https://wanglh39.github.io/marimo-from-scratch/protocol/ch28) |
| 第七篇：前端实现 | ch32-37 | [目录](https://wanglh39.github.io/marimo-from-scratch/frontend/ch32) |
| 第八篇：UI 组件系统 | ch38-41 | [目录](https://wanglh39.github.io/marimo-from-scratch/ui-components/ch38) |
| 第九篇：部署与延伸 | ch42-46 | [目录](https://wanglh39.github.io/marimo-from-scratch/deployment/ch42) |

## 项目结构

```
backend/
├── core/              ← M1: reactive 执行引擎
│   ├── cell.py            Cell 数据结构 + 状态机
│   ├── ast_analyzer.py    AST 提取 defs/refs
│   ├── graph.py           DAG 构建 + 拓扑排序
│   └── executor.py        执行引擎：增量/短路/output
├── storage/           ← M2: .py 文件格式
│   ├── serializer.py      CellGraph → .py
│   └── parser.py          .py → CellGraph
├── components/        ← M4: UI 组件系统
│   └── ui.py              Slider/Button/Checkbox
├── server/            ← M3: WebSocket 后端
│   ├── protocol.py        消息序列化
│   ├── session.py         会话管理 + ui_event
│   └── webapp.py          FastAPI + WebSocket
├── app.py             ← App 类 (.py notebook 直接运行)
frontend/              ← React + TypeScript + CodeMirror 6
docs/                  ← VitePress 文档站 (46 章)
tests/                 ← 79 个测试
examples/              ← 3 个 demo
```

## 里程碑

| 里程碑 | 内容 | 状态 |
|---|---|---|
| M1 | 核心执行引擎（Cell + AST + DAG + 增量执行 + 短路） | ✅ |
| M2 | 文件格式（.py ⇄ notebook 双向转换） | ✅ |
| M3 | WebSocket + React 前端 | ✅ |
| M4 | UI 组件系统（slider/button/checkbox reactive binding） | ✅ |
| M5 | 整合 + 示例 | ✅ |

## 技术栈

- **后端**：Python 3.12 + FastAPI + WebSocket + uv
- **前端**：React 19 + TypeScript + CodeMirror 6 + Vite
- **文档**：VitePress
- **测试**：pytest (79 个测试)

## License

MIT