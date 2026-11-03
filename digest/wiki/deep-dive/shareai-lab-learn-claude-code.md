---
id: deep-dive/shareai-lab-learn-claude-code
title: shareAI-lab/learn-claude-code 深度拆解 - 构建真正 agent 产品的分步教程
description: 深度拆解 shareAI-lab/learn-claude-code：把「构建真正的 agent 产品」拆成可练习步骤，主张 agency 来自模型训练而非外部编排。
date: 2026-11-03
lastModified: 2026-11-03
tags: ["深度拆解", "AI Agent", "教程", "Python", "开源项目"]
categories: ["guides"]
category: guides
locale: zh
slug: shareai-lab-learn-claude-code
author: GitHub Project Manager
summary: shareAI-lab/learn-claude-code 深度拆解：把构建真正 agent 产品拆成 s01-s06 六节可练习课程，适合从头理解 agent 工作原理的开发者。
draft: false
noindex: false
---

# shareAI-lab/learn-claude-code 深度拆解

**仓库**：https://github.com/shareAI-lab/learn-claude-code  
**主要语言**：Python  
**Star**：79.7k · **Fork**：12.7k · **推荐分**：90  
**许可证**：MIT  

## 它到底在做什么

核心观点很尖锐：agency（感知、推理、行动的能力）来自模型训练，而不是外部代码编排。拖拽式工作流、无代码平台、提示词编排库，作者认为它们只是「把 LLM 当成文本补全节点的鲁布·戈德伯格机器」，不是真正的 agent。

但每个 agent 都需要一个环境来运行——Atari 模拟器、Dota 2 客户端、IDE 和终端。模型供给智能，环境供给动作空间。这个仓库教你构建的正是那个「车架（harness）」。

源码结构很干净：`agents/s01_agent_loop.py`、`s02_tool_use.py`、`s03_todo_write.py`、`s04_subagent.py`、`s05_skill_loading.py`、`s06_context_compact.py`，六个文件分别对应 agent 循环、工具调用、待办管理、子 agent、技能加载、上下文压缩，把一个完整 agent 最小可用的能力拆成六节可独立练习的课。

- 主张「模型供智能、环境供动作空间」，两者缺一不可
- 六节课（s01–s06）从 agent 循环到上下文压缩，循序渐进
- 中英文 README 均有（README.md / README-zh.md / README-ja.md），国际化友好

## 适合谁与门槛

适合想亲手理解 agent 内部工作原理、并愿意写 Python 代码实现最小 agent 框架的开发者。

门槛是懂一点 Python，并能接受「先读理论、再写代码」的节奏；如果你只想拖拽搭个流程，可能会觉得这里太偏底层。

## 我的结论

如果你对「agent」一词被滥用感到困惑，这篇值得读。它把 agent 产品拆成「模型（驱动）」+「车架（harness）」，并用 s01–s06 逐步实现。适合想从头理解 agent 工作原理、并亲手写一个最小 agent 框架的开发者；不适合只想拖拽搭建流程的用户。

---
*来源：GitHub 冲浪手记 深度拆解 · 数据来自 GitHub 公开 API*