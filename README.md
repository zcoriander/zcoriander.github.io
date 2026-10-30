# 🌊 GitHub 冲浪手记

一个开源新人的 GitHub 冲浪笔记本 —— 每周收集热门、有趣、有用的开源项目，记录想法与踩坑。

**线上地址**：https://zcoriander.github.io

---

## 这是什么

不是数字看板。榜单数据全部来自 GitHub 公开 API，但每个项目我都真的翻开了 README，
写清楚「它到底在做什么」「为什么这么设计」「上手门槛在哪」。

## 六个分类

| 分类 | 说明 |
|------|------|
| 🔥 本周最热 | 近 30 天新建，增速最快 |
| 🌱 黑马新星 | 三个月内冒头的上升期项目 |
| 🛠️ 新手友好 | 有 good-first-issue，文档友好 |
| 💡 奇思妙想 | 有趣的脑洞，逛着逛着就学会了 |
| 📚 学习资源 | 系统学习路径 |
| 🏛️ 常青经典 | **特殊处理**，见下 |

### 🏛️ 关于「常青经典」的特殊处理

大多数榜单按 star 总数排，结果永远是那几个老面孔——因为它们的 star 早就不涨了，总数自然不动。

所以这一栏换了个思路：

- **配了 token**：用「近 30 天新增 star」排序 → 看谁在悄悄上位
- **未配 token**：`stargazers` 时间戳接口需要认证（返回 401），退化为「近 90 天提交数」→ 看谁还在高强度维护

两种情况下榜单都不会变成老面孔的复制粘贴。

---

## 目录结构

```
.
├── index.html          # 首页（精选 + 分类导航 + 方法论）
├── categories.html     # 完整分类榜
├── deep-dive.html      # 深度拆解
├── about.html          # 关于 + 手记
├── assets/style.css    # 样式
├── data/projects.json  # 采集到的数据 + 文案
├── docs/SECURITY.md    # Token 安全接入指南
└── tools/
    ├── collect.py      # 抓取 + 分类 + 打分
    ├── enrich.py       # 注入人工撰写的深度分析
    ├── build_site.py   # 生成静态页面
    └── gh_api.sh       # Token 安全调用封装
```

## 本地运行

```bash
# 生成站点（纯静态，无需 npm / node）
python3 tools/collect.py    # 抓数据 → data/projects.json
python3 tools/enrich.py     # 注入文案
python3 tools/build_site.py # 生成 HTML

# 本地预览
python3 -m http.server 8000
```

部署由 GitHub Actions 自动完成（`.github/workflows/pages.yml`）：
push 到 `main` → 自动构建 → 自动发布到 GitHub Pages。

## Token

本项目**不需要** token 也能跑（数据来自公开 API），但配了 token 之后：

- API 限额从 60 次/小时 提升到 **5000 次/小时**，搜索从 10 次/分钟 提升到 30 次/分钟
- 能读取 `contributors` 等更细的社区指标，常青榜的「势头分」更准
- **能推送到 `zcoriander.github.io` 并触发 Pages 部署**（需 Contents 写权限）

安全接入方式见 [`docs/SECURITY.md`](docs/SECURITY.md)。

**核心原则：token 只进环境变量或本地受限文件，永不写入仓库、永不进入页面内容。**

当前 token 位置：`~/.config/qwenpaw/github_token`（权限 600），不在仓库内。

> ⚠️ 当前 token 缺少 `zcoriander.github.io` 的 **Contents 写权限**，推送会被拒。
> 修复步骤见 `docs/SECURITY.md` 的「当前阻塞」一节。

---

## 部署

```bash
# 生成站点（纯静态，无需 npm / node）
python3 tools/collect.py    # 抓数据 → data/projects.json
python3 tools/enrich.py     # 注入人工撰写的深度分析
python3 tools/build_site.py # 生成 HTML

# 安全推送（token 经内存态 credential helper，不落盘）
sh tools/push.sh main
```

推送后由 GitHub Actions 自动构建并发布到 GitHub Pages
（`.github/workflows/pages.yml`）。

> 首次部署需要在仓库 **Settings → Pages → Build and deployment**
> 把 Source 设为 **GitHub Actions**。

## 常青榜的特殊处理

大多数榜单按 star 总数排，结果永远是那几个老面孔——因为它们的 star 早就不涨了。

所以这一栏改用「**势头分**」综合排序：

| 信号 | 权重 | 含义 |
|------|------|------|
| 近 90 天 commit 数 | ≤30 | 维护强度 |
| fork / star 比 | ≤25 | 真有人在动手用 |
| 最近提交新鲜度 | ≤20 | 是否还在活跃 |
| 推荐分 | ≤15 | 综合健康度 |
| 贡献者数 | ≤20 | 社区规模 |

> 注：GitHub 的 `stargazers` 时间戳接口对 fine-grained token 返回 403，
> 无法直接计算「近 30 天 star 增量」，故采用上述组合信号。详见 `docs/SECURITY.md`。

## 推荐分算法

不是简单按 star 排。综合考虑：

| 维度 | 权重 | 理由 |
|------|------|------|
| star 规模 | 40 | 对数计分，避免头部碾压 |
| 最近提交 | 25 | 活跃度，7 天内活跃拿满分 |
| fork/star 比 | 15 | fork 说明有人真在动手用 |
| 许可证 | 10 | 有明确许可证才能安全使用 |
| issue 压力 | -10 | 大量未关闭 issue 是维护风险信号 |

## 许可证

站点代码可自由使用。收录的项目版权归各自作者所有，本站仅为索引与学习笔记。

*最后更新：自动生成*
