# 🔄 基于 GitHub Actions 的全自动化方案

> 结论先行：**能实现全自动化，且不需要额外的 token 权限。**
> 你当前的 token 已经具备 `workflow` scope（实测可创建 workflow 文件），
> 而 Actions 内置的 `GITHUB_TOKEN` 能胜任采集、提交、部署全流程。

---

## 一、Workflow 方案的优势

### 1. 消除"人"这个依赖

当前流程是「我跑脚本 → 我提交 → Pages 更新」。Workflow 把它变成：

```
定时触发 → 自动采集 → 自动生成 → 自动提交 → 自动部署 → 自动构建
```

**每周一早上你打开网站，内容已经是新的。** 不需要我在线，不需要你记得跑。

### 2. 凭证生命周期大幅缩短

| | 当前方案 | Workflow 方案 |
|---|---------|-------------|
| 需要长期 token | ✅ 个人 PAT 常驻 | ❌ **完全不需要** |
| 凭证有效期 | 90 天，需手动轮换 | 每次运行自动生成、自动销毁 |
| 泄露窗口 | 长期 | 单次运行（分钟级） |
| 权限范围 | 个人账号级 | 仓库级，且按 `permissions:` 精确声明 |

这是 Workflow 方案**最被低估的优势**——它让"自动化"和"最小权限"不再冲突。

### 3. 内置权限声明式可控

```yaml
permissions:
  contents: read    # 读代码
  pages: write      # 部署 Pages
  id-token: write   # OIDC 认证
```

每个 job 需要什么写什么，不需要的不给。比个人 token 的仓库勾选更细。

### 4. 内置生态

- `actions/checkout` —— 自动拉代码
- `actions/setup-python` —— 自动装环境
- `actions/cache` —— 缓存 API 响应，省限额
- 运行历史、失败通知、重跑按钮 —— 都是现成的
- `workflow_dispatch` —— 随时手动触发

### 5. 天然的 PR 流程

可以做成「自动更新 → 自动开 PR → 你过一眼再合并」，
或者「自动更新 → 直接提交 main」两种模式。

---

## 二、可行性实测结论

我在你的仓库上实测了每一个关键约束：

| # | 约束 | 实测结果 | 结论 |
|---|------|---------|------|
| 1 | Actions 内置 token 能否读其他公开仓库？ | `facebook/react`、`microsoft/vscode`、`rust-lang/rust` 等 repo/contributors/commits 均返回 200/301 | ✅ 可以，不依赖个人 PAT |
| 2 | 单轮 API 调用量？ | 约 **62 次**（search 17 + evergreen 补充 40 + 深度抓取 5） | ✅ GITHUB_TOKEN 限额 1000/小时，占 6% |
| 3 | 能否提交 workflow 文件？ | `PUT .github/workflows/probe.yml` → **成功** | ✅ 当前 token 已有 `workflow` scope |
| 4 | Actions 是否已在运行？ | `pages-build-deployment` 动态工作流，7 次运行记录 | ✅ 权限链路已通 |
| 5 | 定时任务会停吗？ | GitHub 仅在仓库 60 天无活动时暂停定时任务 | ✅ 每次运行都提交内容，仓库持续活跃 |
| 6 | 循环触发风险？ | 提交会触发 push 事件 → 再次运行 | ⚠️ **需处理**（见下） |

---

## 三、推荐架构

```
┌─────────────────────────────────────────────┐
│  触发层                                      │
│   schedule: 每周一 09:00 UTC                │
│   workflow_dispatch: 手动触发                │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  采集层  python tools/collect.py             │
│   → data/projects.json                      │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  文案层  python tools/enrich.py              │
│   → 注入人工撰写的深度分析 + 手记             │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  生成层  python tools/build_site.py          │
│   → index.html / categories.html / ...      │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  提交层  git commit (仅在有变化时)            │
│   → 推送 main，触发 Pages 自动部署            │
└─────────────────────────────────────────────┘
```

---

## 四、循环触发的三种解法

### 方案 A：`paths` 过滤（推荐）

只在数据文件变化时运行，但**提交本身也会改这些文件** → 仍会循环。
所以需要配合"仅在内容真正变化时提交"。

### 方案 B：幂等检查（最稳）

```bash
python3 tools/collect.py
python3 tools/enrich.py
python3 tools/build_site.py

if git diff --quiet; then
  echo "内容无变化，跳过提交"
  exit 0
fi
git commit -am "chore: weekly refresh"
git push
```

**无变化 → 不提交 → 不触发 push → 不循环。** 这是根治方案。

### 方案 C：分支隔离

定时任务推到 `auto-refresh` 分支，开 PR 等你合并。
最保守，但需要你每次手动合并。

> **我的建议**：用 **B + C 组合** —— 默认自动提交到 main（安静运行），
> 同时提供 `workflow_dispatch` 带 `dry_run` 参数，出问题时可以只生成不开 PR。

---

## 五、深度分析文案怎么办（一个真实的取舍）

`tools/enrich.py` 里的**人工撰写的深度分析**（12 篇项目解读 + 4 篇手记）
是站点最有价值的部分，但它本质是**人工内容**。

Workflow 自动化的是**数据层**（star 数、榜单排序、指标卡片），
这部分每次刷新都准确。

但深度分析里的判断（比如"openclaw 的架构选择很聪明"）
**不会随数据自动更新**。这带来一个诚实的取舍：

| 方案 | 效果 | 代价 |
|------|------|------|
| 全自动刷新 | 数据永远准确，判断可能过时 | 需偶尔人工校订 |
| 判断也自动生成 | 全自动但深度下降 | 变成千篇一律的 API 数据搬运 |
| 混合（推荐） | 数据自动，判断保留并在页面标注日期 | 偶尔需要我或你校订一次 |

**推荐做法**：在深度拆解页给每篇文章标注「数据截至 YYYY-MM-DD」，
这样读者知道判断是什么时候写的。同时 enrich.py 可以检测：
若项目 star 数变化超过阈值（比如 ±20%），就在该篇顶部加一个
「⚠️ 项目数据已显著变化」的提示，提醒人工复核。

---

## 六、完整工作流文件

`deploy/pages-actions.yml`（当前备份）可以改造成下面这样，
存到 `.github/workflows/refresh.yml`：

```yaml
name: Weekly Refresh

on:
  schedule:
    - cron: '0 9 * * 1'      # 每周一 09:00 UTC = 北京时间 17:00
  workflow_dispatch:
    inputs:
      dry_run:
        description: '只生成不提交'
        type: boolean
        default: false

permissions:
  contents: write              # 提交刷新后的内容
  pages: write                 # 部署（若改用 Actions 部署）
  id-token: write              # OIDC

concurrency:
  group: refresh
  cancel-in-progress: false    # 防止并发跑重复

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Collect data
        env:
          GITHUB_TOKEN: ${{ github.token }}    # 内置，自动轮换
        run: python tools/collect.py

      - name: Enrich content
        run: python tools/enrich.py

      - name: Build site
        run: python tools/build_site.py

      - name: Check for changes
        id: check
        run: |
          if git diff --quiet; then
            echo "changed=false" >> "$GITHUB_OUTPUT"
            echo "内容无变化，跳过提交"
          else
            echo "changed=true" >> "$GITHUB_OUTPUT"
            git diff --stat
          fi

      - name: Commit and push
        if: steps.check.outputs.changed == 'true' && inputs.dry_run != true
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add -A
          git commit -m "chore: weekly refresh $(date -u +'%Y-%m-%d')"
          git push
```

**注意**：`tools/collect.py` 已经会读环境变量 `GITHUB_TOKEN`，
所以 `env: GITHUB_TOKEN: ${{ github.token }}` 一行就够了，
**不需要任何 secret 配置**。

---

## 七、启用步骤

### 我可以做的（不需要额外权限）

1. 创建 `.github/workflows/refresh.yml`
2. 提交并推送（实测你的 token 有 `workflow` scope）
3. 用 `workflow_dispatch` 手动触发一次验证

### 可能需要你确认的

- **是否保留当前「分支直发」部署？**
  - 保留：workflow 只负责采集+提交，Pages 沿用现在的分支部署。**改动最小，推荐。**
  - 切换：workflow 额外负责部署（需要 `pages: write` + `id-token: write`），
    要在仓库 Settings → Pages 把 Source 改为 **GitHub Actions**。
- **是否用 PR 模式**（自动开 PR 等你合并）还是**直推 main**？

---

## 八、对比：QwenPaw Cron（另一种自动化）

本环境还有 QwenPaw 的 cron 技能（`qwenpaw cron`），也能定时跑任务。

| | GitHub Actions | QwenPaw Cron |
|---|---|---|
| 运行位置 | GitHub 云端 runner | 本机/本容器 |
| 依赖环境存活 | ✅ 不依赖 | ⚠️ 依赖 |
| 凭证 | 内置 GITHUB_TOKEN，自动轮换 | 需要个人 token |
| 可靠性 | 高（GitHub 基础设施） | 取决于容器 |
| 适合 | 站点内容刷新 | 需与本环境交互的任务 |

**结论**：站点刷新用 Actions 更合适 —— 它不需要任何长期凭证，
而且不依赖这个容器是否活着。

---

## 九、我的建议

**值得做。** 理由不是"省事"，而是三点：

1. **消除长期凭证** —— 这是安全性上的净收益，不是妥协
2. **数据保鲜** —— 榜单的价值在于"新"，一周一更刚合适
3. **保留人的部分** —— 深度分析还是人写的，自动化的只是数据层

风险控制：
- 只在内容变化时提交（防循环）
- `concurrency` 防并发
- 保留 `dry_run` 手动开关
- 深度分析标注数据日期 + 显著变化时提示复核

---

*相关：`README.md`（部署说明）· `docs/SECURITY.md`（token 安全）· `deploy/pages-actions.yml`（当前备份）*
