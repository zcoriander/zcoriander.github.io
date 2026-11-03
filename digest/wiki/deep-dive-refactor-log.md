---
id: refactor/deep-dive-2026-11-03
title: 深度拆解内容重构记录 - 基于 anvil-hugo-hexo WikiFrontmatter 规范
description: 记录本次将 12 篇 HTML 格式深度拆解文章重构为 Markdown + WikiFrontmatter 规范的详细改动，包括目录结构、frontmatter 字段、正文迁移及 commit 策略。
date: 2026-11-03
lastModified: 2026-11-03
tags: ["重构记录", "anvil-hugo-hexo", "WikiFrontmatter", "深度拆解", "内容迁移"]
categories: ["guides"]
category: guides
locale: zh
slug: deep-dive-refactor-log
author: GitHub Project Manager
summary: 本次重构将 12 篇 HTML 深度拆解文章迁移为基于 anvil-hugo-hexo WikiFrontmatter 的 Markdown 文件，输出至 digest/wiki/deep-dive/ 目录。
draft: false
noindex: false
---

# 深度拆解内容重构记录

## 重构概述

将原先存储在 `pages/deep-dive/` 下的 12 篇 HTML 格式深度拆解文章，重构为基于 [`anvil-hugo-hexo`](./) 模块 `WikiFrontmatter` schema 的 Markdown 文件，输出至 `digest/wiki/deep-dive/` 目录。

## 为什么重构

原有的深度拆解以独立 HTML 页面形式存在（`pages/deep-dive/{owner}__{repo}.html`），frontmatter 信息散落在 HTML `<head>` 和 `<body>` 中，难以程序化校验，也无法复用到其他平台（Hugo Docs、Hexo Blog）。

基于 `anvil-hugo-hexo` 模块后，所有内容条目可统一通过 `WikiFrontmatter` 验证，并使用 `toPlatformFrontmatter()` 转换为各平台专用 frontmatter，实现「一次撰写，多平台发布」。

## 改动明细

### 新增目录

```
digest/wiki/deep-dive/
├── index.md                          # 深度拆解索引（12 篇文章导航）
├── openclaw-openclaw.md              # openclaw/openclaw - 本地 AI 助手 Gateway
├── obra-superpowers.md               # obra/superpowers - 编码 agent 开发方法论
├── mattpocock-skills.md              # mattpocock/skills - 轻量 agent 技能集合
├── shareai-lab-learn-claude-code.md  # shareAI-lab/learn-claude-code - agent 构建教程
├── ssloy-tinyrenderer.md             # ssloy/tinyrenderer - 裸 C++ 软件渲染器
├── codecrafters-io-build-your-own-x.md # codecrafters-io/build-your-own-x - 从零实现教程索引
├── donnemartin-system-design-primer.md # donnemartin/system-design-primer - 系统设计指南
├── freecodecamp-freecodecamp.md      # freeCodeCamp/freeCodeCamp - 免费编程教育
├── firstcontributions-first-contributions.md # firstcontributions/first-contributions - 开源入门 PR 指南
├── seedds-nxnative.md                # seedds/nxnative - Apple 芯片原生运行 Switch 游戏
├── storytold-effectcraft.md          # storytold/effectcraft - 纯 Rust 动态图形合成器
├── simbasjungles-free-my-tv.md       # simbasjungles/free-my-tv - 无广告电视主屏幕
└── deep-dive-refactor-log.md         # 本重构记录（当前文件）
```

### Frontmatter 规范化

每篇文章的 frontmatter 均严格对齐 `anvil-hugo-hexo` 的 `WikiFrontmatter`：

| 字段 | 来源 | 说明 |
|------|------|------|
| `id` | 新生成 | `deep-dive/{slug}` 格式，全局唯一 |
| `title` | HTML `<h1>` | 文章标题，1–80 字符 |
| `description` | HTML `.deep-lead` | 元描述，40–165 字符 |
| `date` | 新生成 | `2026-11-03`（重构日期） |
| `lastModified` | 新生成 | `2026-11-03` |
| `tags` | 从 HTML 内容提取 | 项目相关标签数组 |
| `categories` | 固定值 | `["guides"]` |
| `category` | 固定值 | `"guides"`（WikiCategory 枚举） |
| `locale` | 固定值 | `"zh"` |
| `slug` | 新生成 | URL 友好的标识符 |
| `author` | 固定值 | `GitHub Project Manager` |
| `summary` | 从 HTML 结论提取 | 最多 400 字符的一句话总结 |
| `draft` | 固定值 | `false` |
| `noindex` | 固定值 | `false` |

### 正文结构统一

每篇 Markdown 文章保留原 HTML 的核心章节，并统一为以下结构：

1. 页面头部（仓库链接、语言、Star/Fork、推荐分、许可证）
2. `## 它到底在做什么` —— 核心功能描述
3. `## 架构/设计判断`（如有）—— 值得关注的技术选型
4. `## 适合谁与门槛` —— 目标读者与上手难度
5. `## 我的结论` —— 个人使用建议与适用场景
6. 来源注脚

部分文章保留了原 HTML 中特有的章节，如：
- `openclaw-openclaw.md`：`## 安装与日常门槛`
- `codecrafters-io-build-your-own-x.md`：`## 实际使用建议`
- `donnemartin-system-design-primer.md`：`## 如何用好它`
- `freecodecamp-freecodecamp.md`：`## 学习建议`
- `firstcontributions-first-contributions.md`：`## 你会学到什么，以及下一步`

## 索引页更新

新增 `digest/wiki/deep-dive/index.md` 作为深度拆解索引，包含 12 篇文章的导航表格（项目、语言、Star、推荐分、一句话定语）。

## Commit 策略（本次决定）

考虑到本次改动涉及 13 个新 Markdown 文件（12 篇文章 + 1 篇索引）+ 1 篇重构记录，体量较大，我决定：

| Commit | 内容 | 说明 |
|--------|------|------|
| `feat: 重构深度拆解内容为 WikiFrontmatter 规范` | 12 篇文章 md + index.md | 主要内容重构 |
| `docs: 记录深度拆解重构改动说明` | deep-dive-refactor-log.md | 单独记录改动，便于后续回溯 |

两个 commit 后推送到 GitHub 主分支。

## 后续可选工作

- 使用 `anvil-hugo-hexo` 的 `validateFrontmatter()` 批量校验所有 frontmatter 合规性
- 使用 `toPlatformFrontmatter()` 将 wiki 条目转换为 Hugo Docs / Hexo Blog 格式，实现跨平台同步
- 将 `pages/deep-dive.html` 索引页改为从 `digest/wiki/deep-dive/index.md` 动态生成

---
*本重构记录基于 anvil-hugo-hexo v0.1.0 模块 schema 编写*