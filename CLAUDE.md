# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

mas-ass 是一个**基于 MCP 协议的多 Agent 协作系统**（课程项目/作业）。

- **输入**：用户的一个问题或需求（如"帮我写一篇关于 AI Agent 的文章"）
- **输出**：多个 Agent 协作完成 研究 → 撰写 → 审核 → 润色，最终产出一篇成稿
- **扩展项**：失败重试机制（技术重试 + 质量重试）

## 架构（已讨论定稿）

- **编排**：LangGraph **固定图**（节点 + 边），**不是** agent-to-agent 自由协作。
  理由：步骤基本预先定死，固定图好控制、好演示、好 debug。
  控制流（谁先谁后、审核不通过回哪、重试几次）全部由 LangGraph 的**边**负责。
- **MCP 定位**：MCP = **工具/资源接入层**（"读法 A"），藏在 agent 底下，**不是** agent 之间的通信总线。
  真正用到 MCP 的是 **research agent** —— 调 web search MCP server 取资料。
  agent 之间的"交接"靠**共享 state**，不靠 MCP。

### 节点与条件边
`research → writer → reviewer →(条件边)→ polish → 结束`
- reviewer 判定不通过时，按结构化结论的 `level` 路由：
  - `needs_rewrite` → 回 writer（带 feedback 重写）
  - `needs_research` → 回 research（资料/论据不足，重新找）
- **质量重试上限 3 次**（防无限循环 + 防烧 token）

### 关键设计决策（答辩要能讲清楚）
- **双重重试**：
  - **技术重试**：LLM 调用超时 / API 报错 / 限流 → 指数退避重调（与内容无关，一个重试装饰器搞定）
  - **质量重试**：审核不通过 → 把修改意见喂回 writer 重写，上限 3 次
- **审核 agent 的可靠性**（审核本身也是概率模型）：
  - 明确基准：对照"**用户明确化的需求清单**"逐条核对，而非凭感觉打分
  - 温度调低 / 归零，减少随机性
  - **强制结构化输出** JSON：`{passed, level: "needs_rewrite"|"needs_research", feedback}` —— 只有结构化，条件边才能可靠路由
  - 用户需求没说清 → 先反问；实在随便 → 用预设基本要求先出初稿，再迭代
- **3 次用完仍不通过的兜底**：放行最后一版 + **明确列出仍未通过的点**（human-in-the-loop 作为下一步延伸）。
  demo 主路径不停下来等用户（否则现场拖时间）。

### 共享 state（agent 间交接载体 = LangGraph state）
- 用户原始需求（+ 明确化后的需求清单）
- research 产出（**结构化要点 + 每条来源**，不是原文堆砌）
- writer 稿子（当前版本）
- reviewer 结论（结构化 JSON）
- 质量重试计数

> 串行流水线：同一时刻只有一个 agent 在跑，**不需要锁 / 不需要谁"通知"谁**，接力全由编排器负责。
> （"锁 + 通知"是并发协作 agent 的模型，本系统用不上，别自己再写一套，会与 LangGraph 控制流打架。）

### research 产出的处理
research 搜回来的内容**先提炼**成结构化要点 + 来源，再交给 writer（不全塞原文）——省 token、去噪音、避免 writer 在一堆原文里迷失 / 超上下文窗口。

## 技术栈（规划中，开工时确认）
- 语言：Python（PyCharm 里 SDK 名为 `langchain`）
- 编排：LangGraph
- MCP：1 个 web search MCP server（作业友好型：**SearXNG 自托管** 或 **DuckDuckGo 免 key**，先确认是否要 API key / 付费）+ 对应的 MCP client adapter
- LLM：建议 Claude（主力 Sonnet 保证质量；研究环节可用轻量模型省 token）—— 开工时定具体 model ID
- 现状：尚未初始化 git，无依赖清单、无测试 —— 开工后在此补充 安装 / 运行 / 测试 命令

## 协作约定
- 使用中文交流与注释
- 新功能先出设计文档 / 方案，确认后再动手
- 代码按模块逐个编写，每个模块确认后再继续下一个
- 代码写详细的逻辑说明和注释
- 修改认证相关代码前主动提示安全影响

## 待补充（开工后更新）
1. 依赖管理方式（requirements.txt / pyproject.toml）与安装命令
2. 运行方式、跑测试、跑单个测试
3. 实际代码结构 / 模块划分
