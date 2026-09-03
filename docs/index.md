---
hero:
  name: marimo-from-scratch
  text: 从零实现 reactive notebook
  tagline: 理解 marimo 的底层原理与设计哲学 · 46 章详尽文档 · 约 5000 行代码
  actions:
    - theme: brand
      text: 开始阅读
      link: /overview/ch01
    - theme: alt
      text: GitHub
      link: https://github.com/wanglh39/marimo-from-scratch
---

## 这是什么？

一个教学项目，从零复刻 [marimo](https://github.com/marimo-team/marimo) 的核心功能，通过 **46 章文档** 讲透 reactive notebook 的底层原理。

## 核心原理一句话

> AST 静态分析提取 cell 的变量定义/引用 → 构建 DAG → 拓扑排序 + 增量执行 + 短路 = reactive

## 里程碑

| 里程碑 | 内容 | 代码 |
|---|---|---|
| M1 | 核心执行引擎 | `backend/core/` |
| M2 | .py 文件格式 | `backend/storage/` |
| M3 | WebSocket + React 前端 | `backend/server/` + `frontend/` |
| M4 | UI 组件系统 | `backend/components/` |
| M5 | 整合 + 示例 | `examples/` |

## 技术栈

- **后端**：Python 3.12 · FastAPI · WebSocket · uv
- **前端**：React 19 · TypeScript · CodeMirror 6 · Vite
- **文档**：VitePress
- **测试**：pytest (79 个测试全通过)