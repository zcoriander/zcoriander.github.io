---
id: deep-dive/storytold-effectcraft
title: storytold/effectcraft 深度拆解 - 纯 Rust 开源动态图形与视觉特效工作室
description: 深度拆解 storytold/effectcraft：用纯 Rust 写的开源专业动态图形与视觉特效合成器，支持 308 个效果、图层、关键帧、3D 摄像机。
date: 2026-11-03
lastModified: 2026-11-03
tags: ["深度拆解", "动态图形", "视觉特效", "Rust", "开源项目"]
categories: ["guides"]
category: guides
locale: zh
slug: storytold-effectcraft
author: GitHub Project Manager
summary: storytold/effectcraft 深度拆解：纯 Rust 写的跨平台开源合成/特效工具，目标是免费开源的 After Effects 替代方案。
draft: false
noindex: false
---

# storytold/effectcraft 深度拆解

**仓库**：https://github.com/storytold/effectcraft  
**主要语言**：Rust  
**Star**：8.3k · **Fork**：（未标注） · **推荐分**：（未标注）  
**许可证**：MIT OR Apache-2.0  

## 它到底在做什么

EffectCraft 是一个合成器：合成、图层、关键帧、308 个内置效果、图层样式、表达式、3D 摄像机和灯光、渲染队列，覆盖了动态图形与视觉特效工作室的核心能力。原生支持 macOS、Windows、Linux，也能跑在浏览器里，跨平台能力较强。

仓库用纯 Rust 写（`.cargo/config.toml`、`AGENTS.md`、`CLAUDE.md`），CI 覆盖 freebsd、nix、windows-arm64 等平台，有 release 和 packaging-lint 工作流，说明作者把多平台发布当成了长期目标。`ATTRIBUTION.md` 列出了第三方依赖的许可证归属，工程规范意识较强。

CodeRabbit 自动审查 PR，SonarCloud 扫描代码质量，Discord 有社区交流，这些表明它不是一个随便写写的玩具，而是有意往专业工具方向走的项目。

- 纯 Rust，跨平台（macOS/Windows/Linux + 浏览器）
- 308 个效果、图层、关键帧、表达式、3D 摄像机/灯光、渲染队列
- MIT OR Apache-2.0 双许可，CodeRabbit + SonarCloud 工程治理

## 适合谁与门槛

适合想要免费开源的专业合成/特效工具、愿意尝试年轻快速迭代项目的人；也适合 Rust 爱好者参与贡献。

门槛是「接受年轻项目可能不稳定」；如果你需要 After Effects 级别的稳定性和生态（插件、模板、官方支持），这个项目还不够。

## 我的结论

一个用 Rust 写的、跨平台的开源合成/特效工具，目标是「免费、开源、专业」的 After Effects 替代方案。它还很年轻（自称 young and moving fast），已可用但不免有不稳定之处。适合想要免费开源的动态图形/特效工具、愿意尝试年轻项目的人；不适合需要生产级稳定性的商业用户。CodeRabbit 审查 PR、SonarCloud 扫描代码，说明项目在工程规范上有投入。

---
*来源：GitHub 冲浪手记 深度拆解 · 数据来自 GitHub 公开 API*