---
id: deep-dive/ssloy-tinyrenderer
title: ssloy/tinyrenderer 深度拆解 - 裸 C++ 软件渲染器从零实现教程
description: 深度拆解 ssloy/tinyrenderer：用约 500 行 C++ 从零写软件渲染器，配套 14 篇课程笔记，教图形库内部工作原理。
date: 2026-11-03
lastModified: 2026-11-03
tags: ["深度拆解", "3D 图形", "渲染器", "C++", "开源项目"]
categories: ["guides"]
category: guides
locale: zh
slug: ssloy-tinyrenderer
author: GitHub Project Manager
summary: ssloy/tinyrenderer 深度拆解：裸 C++ 从零写软件渲染器，配套 14 篇讲义，教图形库内部工作原理。
draft: false
noindex: false
---

# ssloy/tinyrenderer 深度拆解

**仓库**：https://github.com/ssloy/tinyrenderer  
**主要语言**：C++  
**Star**：24.5k · **Fork**：2.3k · **推荐分**：60  
**许可证**：NOASSERTION  

## 它到底在做什么

这是一个软件渲染器教程：不使用任何第三方图形库（尤其是图形相关的），只用 C++ 从零实现，最终生成一张渲染好的 3D 模型图片。输入是三角网格和纹理，输出是一张图，没有图形界面。

作者把现代图形管线拆成了可独立学习的小步：Bresenham 线段算法、三角形光栅化、重心坐标入门、隐面移除、相机处理（两个版本）、着色、纹理、切线空间法线贴图、阴影映射、间接光照，最后有 toon shading 奖励关。

仓库很小：`geometry.h`、`main.cpp`、`model.cpp`、`model.h` 几个核心文件，外加一个单类 TGA 图像处理器（RGB/RGBA/灰度），以及 `obj/african_head/` 下的示例模型与贴图。从「只能给一个像素上色」开始，线段、三角形都要自己手动实现。

- 约 500 行 C++，学生通常需 10–20 小时才能做出像样的渲染器
- 配套 14 篇课程笔记（haqr.eu/tinyrenderer），作者说「代码本身没什么意思，看笔记」
- 明确声明：不打算教怎么写 GPU 应用，只想教图形库内部工作原理

## 适合谁与门槛

适合想理解 3D 图形底层原理、愿意从零手写渲染器、不怕 C++ 和一点线性代数的人。

门槛是 C++ 基础和能看懂讲义的英文；如果你只想调用现成的图形 API 做东西，这仓库对你帮助不大。

## 我的结论

它想教你的不是「怎么调用 OpenGL/Vulkan/Metal/DirectX」，而是「这些图形库内部到底是怎么工作的」。适合想从底层理解 3D 图形、愿意动手写渲染器的人；代码本身作者说「没什么意思」，真正的价值是配套的 14 篇讲义；不适合想做现代 GPU 应用开发的人（作者明确说不展示如何写 GPU 应用）。

---
*来源：GitHub 冲浪手记 深度拆解 · 数据来自 GitHub 公开 API*