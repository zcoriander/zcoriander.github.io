---
id: deep-dive/simbasjungles-free-my-tv
title: simbasjungles/free-my-tv 深度拆解 - 无广告电视主屏幕替代方案
description: 深度拆解 simbasjungles/free-my-tv：为 Google TV/LG webOS/Samsung Tizen 打造的快速、无广告电视主屏幕，Built with Claude Code。
date: 2026-11-03
lastModified: 2026-11-03
tags: ["深度拆解", "电视应用", "无广告", "Claude Code", "AI 编程", "开源项目"]
categories: ["guides"]
category: guides
locale: zh
slug: simbasjungles-free-my-tv
author: GitHub Project Manager
summary: simbasjungles/free-my-tv 深度拆解：无广告电视主屏幕替代方案，Built with Claude Code，60 fps、96 MB 内存。
draft: false
noindex: false
---

# simbasjungles/free-my-tv 深度拆解

**仓库**：https://github.com/simbasjungles/free-my-tv  
**主要语言**：Java  
**Star**：5.7k · **Fork**：972 · **推荐分**：87.5  
**许可证**：MIT  

## 它到底在做什么

Free My TV 是一套替代电视原厂主屏幕的方案，支持 Google TV / Android TV（Android 8+）、LG webOS、Samsung Tizen。核心卖点：**无广告、无赞助行、无自动播放促销**；把你实际用的 App 排在玻璃搁架上，你定顺序；每小时三个来自你已安装 App 的非赞助精选；有 Continue Watching、天气、加密货币价格、跟随日落的明暗模式、屏保、自己的照片/screensaver 等功能。

仓库里 `app/` 是 Android 工程（`AndroidManifest.xml`、`assets/` 字体与 i18n 多语言 JSON、`.github/` 工作流 `check.yml`/`pages.yml`），`AGENTS.md` 和 `CLAUDE.md` 说明它是面向 AI 编程助手维护的，**Built with Claude Code**。README 里甚至写了「One button to undo」——一键恢复出厂主屏，降低试用风险。

性能数据写在 README 里：60 fps，每帧 16.6 ms，96 MB 内存（对比原厂 242 MB，省 60%），在 98 英寸 TCL Google TV (Android 14) 上测得。

- 无广告、无赞助行、无自动播放促销
- Built with Claude Code，AI 编程构建的实用端侧应用
- 60 fps、96 MB 内存、多语言 i18n、一键恢复出厂主屏

## 适合谁与门槛

适合厌恶电视厂商主屏幕广告、愿意花十几分钟侧载 APK 到 Google TV/Android TV 的人；也适合想看「AI 编程做一个真实 TV 应用」案例的开发者。

门槛：需要一台 Google TV/Android TV（Android 8+）和同 Wi-Fi 的电脑，APK 装在电视而非手机；没有智能电视的用户用不上。

## 我的结论

这是一个「把电视主屏幕夺回来」的开源 App：无广告、无赞助行、无自动播放促销，你的 App 前面和中心，精选内容来自你已安装的 App 而非赞助。它是用 Claude Code 构建的（Built with Claude Code），是 AI 编程做实用端侧应用的一个参考案例。60 fps、96 MB 内存（远低于原厂 242 MB），有多语言 i18n。适合厌恶厂商广告主屏幕、愿意花十几分钟侧载的人；不适合没有智能电视的用户。

---
*来源：GitHub 冲浪手记 深度拆解 · 数据来自 GitHub 公开 API*