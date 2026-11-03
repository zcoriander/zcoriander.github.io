---
id: deep-dive/obra-superpowers
title: obra/superpowers 深度拆解 - 编码 agent 软件开发方法论
description: 深度拆解 obra/superpowers：一套给编码 agent 用的软件开发方法论，可组合的技能 + 初始指令，让 agent 在动手写代码前先过需求、设计、计划。
date: 2026-11-03
lastModified: 2026-11-03
tags: ["深度拆解", "AI Agent", "开发方法论", "开源项目"]
categories: ["guides"]
category: guides
locale: zh
slug: obra-superpowers
author: GitHub Project Manager
summary: obra/superpowers 深度拆解：给编码 agent 用的软件开发方法论，让 agent 在动手写代码前先把需求、设计、计划过一遍。
draft: false
noindex: false
---

# obra/superpowers 深度拆解

**仓库**：https://github.com/obra/superpowers  
**主要语言**：Shell  
**Star**：310.6k · **Fork**：27.6k · **推荐分**：87  
**许可证**：MIT  

## 它到底在做什么

Superpowers 是一套完整的软件开发方法论，建立在可组合的 skills 和一些初始指令之上。核心思想是：agent 一启动就不该立刻写代码，而应该先退一步，跟你把「到底想做什么」讲清楚。

具体流程是：从对话中提炼规格（spec）、以可读的分块展示给你确认、签字后生成实现计划、再启动「子驱动开发」（subagent-driven-development），让多个子 agent 分工完成每项工程任务、互相检查、审查。

仓库按 agent 平台拆分了插件：`.claude-plugin`、`.codex-plugin`、`.cursor-plugin`、`.devin-plugin`、`.opencode/plugins/superpowers.js`、`.pi/extensions/superpowers.ts`、`.kimi-plugin`、`.hermes-plugin`、`.muse-plugin`，以及 `.agents/plugins/marketplace.json` 技能市场。说明它刻意做到了「在哪个 agent 里都能用」，而不是锁死单一平台。

- 强调真 red/green TDD、YAGNI（你不需要它）、DRY
- 计划写得足够清楚，让「一个没有项目背景、品味差、讨厌测试的初级工程师」都能照着做
- agent 可自主工作数小时而不偏离计划

## 适合谁与门槛

适合已经把 agent 当成日常编程伙伴、并希望提升代码质量与可复现性的团队或个人。

门槛不高（它本质是插件 + 指令），但要落地需要团队愿意接受「先写 spec、再写 code」的节奏，以及对子 agent 产出做审查的习惯。

## 我的结论

它不是一个新编程语言，也不是一个 IDE，而是一套「让 agent 慢下来再动手」的方法论。对已经在用 Claude Code / Codex / Cursor 等 agent 的团队，值得把它当成标准作业程序（SOP）引入；对只偶尔写脚本的个人，则可能过于沉重。

---
*来源：GitHub 冲浪手记 深度拆解 · 数据来自 GitHub 公开 API*