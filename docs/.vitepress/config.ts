import { defineConfig } from 'vitepress'
import mathjax3 from 'markdown-it-mathjax3'

export default defineConfig({
  title: 'marimo-from-scratch',
  description: '从零实现 marimo：理解 reactive notebook 的底层原理与设计哲学',
  lang: 'zh-CN',
  cleanUrls: true,
  markdown: {
    config: (md) => {
      md.use(mathjax3)
    },
  },
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: 'GitHub', link: 'https://github.com/wanglh39/marimo-from-scratch' },
    ],
    sidebar: [
      {
        text: '第一篇：背景与动机',
        collapsed: false,
        items: [
          { text: 'ch01 - 什么是 marimo', link: '/overview/ch01' },
          { text: 'ch02 - Jupyter 的痛点', link: '/overview/ch02' },
          { text: 'ch03 - reactive 编程范式', link: '/overview/ch03' },
          { text: 'ch04 - marimo 设计哲学', link: '/overview/ch04' },
          { text: 'ch05 - 整体架构总览', link: '/overview/ch05' },
        ],
      },
      {
        text: '第二篇：Cell 与 AST 分析',
        collapsed: false,
        items: [
          { text: 'ch06 - Cell 数据结构', link: '/cell-ast/ch06' },
          { text: 'ch07 - 为什么用 AST', link: '/cell-ast/ch07' },
          { text: 'ch08 - AST 遍历实战', link: '/cell-ast/ch08' },
          { text: 'ch09 - 提取 defs 与 refs', link: '/cell-ast/ch09' },
          { text: 'ch10 - 作用域与边界情况', link: '/cell-ast/ch10' },
          { text: 'ch11 - 完整分析示例', link: '/cell-ast/ch11' },
        ],
      },
      {
        text: '第三篇：DAG 构建',
        collapsed: false,
        items: [
          { text: 'ch12 - 图论基础', link: '/dag/ch12' },
          { text: 'ch13 - 从 cell 构建 DAG', link: '/dag/ch13' },
          { text: 'ch14 - 循环依赖检测', link: '/dag/ch14' },
          { text: 'ch15 - 依赖查询：祖先与后代', link: '/dag/ch15' },
          { text: 'ch16 - DAG 可视化与调试', link: '/dag/ch16' },
        ],
      },
      {
        text: '第四篇：执行引擎',
        collapsed: false,
        items: [
          { text: 'ch17 - 拓扑排序：Kahn 算法', link: '/execution/ch17' },
          { text: 'ch18 - 增量执行：脏节点传播', link: '/execution/ch18' },
          { text: 'ch19 - 短路机制', link: '/execution/ch19' },
          { text: 'ch20 - 命名空间管理', link: '/execution/ch20' },
          { text: 'ch21 - 并行执行的可能性', link: '/execution/ch21' },
          { text: 'ch22 - output 与 stdout 提取', link: '/execution/ch22' },
        ],
      },
      {
        text: '第五篇：文件格式',
        collapsed: false,
        items: [
          { text: 'ch23 - .py 即 notebook', link: '/file-format/ch23' },
          { text: 'ch24 - 函数签名编码依赖', link: '/file-format/ch24' },
          { text: 'ch25 - parser 实现', link: '/file-format/ch25' },
          { text: 'ch26 - serializer 实现', link: '/file-format/ch26' },
          { text: 'ch27 - 与 .ipynb 对比', link: '/file-format/ch27' },
        ],
      },
      {
        text: '第六篇：通信协议',
        collapsed: false,
        items: [
          { text: 'ch28 - 为什么 WebSocket', link: '/protocol/ch28' },
          { text: 'ch29 - 消息协议设计', link: '/protocol/ch29' },
          { text: 'ch30 - cell 状态机', link: '/protocol/ch30' },
          { text: 'ch31 - 断线重连', link: '/protocol/ch31' },
        ],
      },
      {
        text: '第七篇：前端实现',
        collapsed: false,
        items: [
          { text: 'ch32 - React 与 reactive', link: '/frontend/ch32' },
          { text: 'ch33 - CodeMirror 6 集成', link: '/frontend/ch33' },
          { text: 'ch34 - Cell 组件', link: '/frontend/ch34' },
          { text: 'ch35 - 输出渲染', link: '/frontend/ch35' },
          { text: 'ch36 - 前后端状态同步', link: '/frontend/ch36' },
          { text: 'ch37 - 交互设计', link: '/frontend/ch37' },
        ],
      },
      {
        text: '第八篇：UI 组件系统',
        collapsed: false,
        items: [
          { text: 'ch38 - 组件设计理念', link: '/ui-components/ch38' },
          { text: 'ch39 - slider 完整实现', link: '/ui-components/ch39' },
          { text: 'ch40 - reactive binding', link: '/ui-components/ch40' },
          { text: 'ch41 - 组件组合与布局', link: '/ui-components/ch41' },
        ],
      },
      {
        text: '第九篇：部署与延伸',
        collapsed: false,
        items: [
          { text: 'ch42 - 从 notebook 到 web app', link: '/deployment/ch42' },
          { text: 'ch43 - FastAPI 服务架构', link: '/deployment/ch43' },
          { text: 'ch44 - GitHub Pages 文档站', link: '/deployment/ch44' },
          { text: 'ch45 - CI/CD 自动部署', link: '/deployment/ch45' },
          { text: 'ch46 - 源码导读与对比', link: '/deployment/ch46' },
        ],
      },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/wanglh39/marimo-from-scratch' },
    ],
  },
})