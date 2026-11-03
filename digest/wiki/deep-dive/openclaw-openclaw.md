---
id: deep-dive/openclaw-openclaw
title: openclaw/openclaw 深度拆解 - 本地 AI 助手 Gateway 架构与跨渠道部署
description: 深度拆解 openclaw/openclaw：本地跑的 AI 助手 + Gateway 控制平面，支持 Discord/iMessage/Slack/Teams/Telegram/WhatsApp 等 20 多个渠道，架构上「策略由代码强制」。
date: 2026-11-03
lastModified: 2026-11-03
tags: ["深度拆解", "AI Agent", "Gateway", "开源项目"]
categories: ["guides"]
category: guides
locale: zh
slug: openclaw-openclaw
author: GitHub Project Manager
summary: openclaw/openclaw 深度拆解：本地 AI 助手部署方案，支持 20+ 聊天渠道，架构核心为「策略由代码强制」。
draft: false
noindex: false
---

# openclaw/openclaw 深度拆解

**仓库**：https://github.com/openclaw/openclaw  
**主要语言**：TypeScript  
**Star**：393.6k · **Fork**：82.7k · **推荐分**：87  
**许可证**：MIT  

## 它到底在做什么

一句话：本地跑的 AI 助手，外加一个叫 Gateway 的控制平面。Gateway 负责会话、工具调用、事件和渠道连接；助手本体通过插件机制对接 Claude、Codex 或本地模型。

关键点是它不打算取代你的聊天软件，而是「住进去」。个人版跑在笔记本上，团队版跑在服务器上——作者说区别只是配置文件。

- 状态、记忆、凭证全部留在自己硬件上，不上云
- 模型是可替换插件，换 Claude/Codex/本地模型不用动其他配置
- 由 OpenClaw Foundation（501(c)(3) 独立基金会）托管，没有付费层、没有托管服务、没有代币

## 让我在意的架构选择

README 里有一句话我反复看了两遍：**trusted gateway, untrusted execution, policy enforced by code**——可信网关、不可信执行、策略由代码强制。

这和很多「把 Agent 塞进沙箱里跑」的方案是反的。它的思路是：执行环境（工具、命令、文件）是不可信边界内的，所以权限判定必须在网关这一层用代码写死，而不是指望被调用的那部分自觉。

仓库里的 `.agents/skills/` 目录下按能力划分了大量技能（agent-transcript、auto-qa、autoreview、claw-score 等），claw-score 下还细分了 references/completeness/agent-runtime、android-app、anthropic-provider-path 等子目录，说明它把「agent 能力评分」本身也做成了可插拔的技能体系，而非写死在核心里。

## 安装与日常门槛

一条 curl 命令（`curl -fsSL https://openclaw.ai/install.sh | bash`）或一条 npm 命令，跨 macOS / Linux / Windows，安装时会自动把缺失的 Node.js 运行时装上。

已自带 Node.js 的用户可直接 `npm install -g openclaw@latest`，要求 Node 24.22.1+ 或 26.12.1+，这算是个小门槛，但换来的是不用自己拼装依赖。

装完自动跑引导流程：验证模型连通性、创建工作区、配置 Gateway。默认只做每日版本检查，匿名功能统计是 opt-in，`update.checkOnStart: false` 可把遥测完全关掉——对一个要常驻在你所有聊天窗口里的东西，这个默认值是加分项。

## 我的结论

如果你想要一个「常驻在聊天软件里的私人助手」，目前生态里最完整的开源方案之一。架构上「策略由代码强制」那句话值得所有做 Agent 的人抄在墙上。适合有一定技术基础、愿意自己管一台机器的人；完全零基础的话，20 多个渠道的配置量会有点劝退。

---
*来源：GitHub 冲浪手记 深度拆解 · 数据来自 GitHub 公开 API*