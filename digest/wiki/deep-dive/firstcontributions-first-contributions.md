---
id: deep-dive/firstcontributions-first-contributions
title: firstcontributions/first-contributions 深度拆解 - 开源新手第一个 PR 指南
description: 深度拆解 firstcontributions/first-contributions：让第一次参与开源的人尽快完成第一个 Pull Request，60 多种语言翻译。
date: 2026-11-03
lastModified: 2026-11-03
tags: ["深度拆解", "开源入门", "PR 指南", "贡献指南", "开源项目"]
categories: ["guides"]
category: guides
locale: zh
slug: firstcontributions-first-contributions
author: GitHub Project Manager
summary: firstcontributions/first-contributions 深度拆解：开源新手提交第一个 PR 的起点，门槛极低，60 多种语言翻译。
draft: false
noindex: false
---

# firstcontributions/first-contributions 深度拆解

**仓库**：https://github.com/firstcontributions/first-contributions  
**主要语言**：（未标注）  
**Star**：56.7k · **Fork**：112.1k · **推荐分**：90  
**许可证**：MIT  

## 它到底在做什么

core 只有一件事：把你的名字加到 `Contributors.md`，然后提一个 PR。仓库提供贡献指南（`CONTRIBUTING.md`）、行为准则（`CODE_OF_CONDUCT.md`）、PR 模板，还有各语言翻译的文档（`docs/translations/` 下有阿尔巴尼亚语、亚美尼亚语、乌兹别克语……一直到中文简体/繁体、俄语、阿拉伯语等几十种），降低语言障碍。

`.github/workflows/auto-pr-merge.yml` 负责把符合条件的 PR 自动合并，维护者不需要逐个手动审核，这也意味着你的 PR 大概率会被快速接收，适合拿来练手、拿到第一个「已合并」徽章。

- 门槛极低：改一个 Markdown 文件就完成第一个 PR
- 60 多种语言翻译，面向全球新手
- 自动 PR 合并工作流，新手 PR 被接收概率高

## 适合谁与门槛

适合完全没有开源经验、想把第一个 PR 「刻在纪念碑上」的人；也适合老师/社区组织者带新手练手。

门槛几乎为零：会 Git 基本操作（fork、改文件、提 PR）即可；但完成这个 PR 后，你还需要学习如何读一个真实项目、如何审查代码、如何和维护者沟通。

## 你会学到什么，以及下一步

做完这个 PR 你会掌握开源贡献的最小闭环：fork 仓库、创建分支、改文件、提 PR、回应 review、被合并。这是参与任何大型开源项目的通用技能。

建议在此之后不要停在这里：找一个你实际在用的项目，翻开它的 Good First Issue，读一遍 README 的贡献指南，再尝试提第二个 PR。第一个 PR 是门票，不是终点。

## 我的结论

如果你还没给开源社区提过第一个 PR，这是最常被推荐的起点：门槛极低，改一个文件（往 `Contributors.md` 加一行名字）就能完成一次完整的「 fork → 改改 → 提 PR → 被合并 」流程。多语言翻译覆盖几十种语言，说明它是面向全球零基础新手的；但它只是入门，真正参与一个项目还需要之后学更多。

---
*来源：GitHub 冲浪手记 深度拆解 · 数据来自 GitHub 公开 API*