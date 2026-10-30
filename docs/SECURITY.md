# 🔐 GitHub Token 安全接入指南

> 目标：**Token 永远不进入 LLM 上下文，不出现在聊天记录，不写进任何 Git 仓库。**

---

## ✅ 当前状态：已上线

**线上地址**：https://zcoriander.github.io （已验证可访问，HTTP 200）

| 项目 | 状态 |
|------|------|
| Token 类型 | Fine-grained PAT（`github_pat_` 前缀），93 字符 |
| 认证身份 | `zcoriander`（User） |
| Token 位置 | `~/.config/qwenpaw/github_token`（权限 600），**不在工作区内** |
| API 限额 | **5000 次/小时**（未认证 60）、搜索 **30 次/分钟**（未认证 10） |
| 公开仓库读取 | ✅ repo / commits / contributors 正常 |
| `zcoriander.github.io` 写入 | ✅ Contents(RW) 已授权，推送成功 |
| Pages 部署 | ✅ 分支直发（main 分支根目录），status = `built` |
| 工作区残留 | 无（token 已迁至 `~/.config/qwenpaw/`，原文件移入 `.local-secrets/` 备份） |

验证：

```bash
sh tools/gh_api.sh --auth-only
# → auth: token present (source: file:/root/.config/qwenpaw/github_token)
# → rate_limit_probe_http: 200
```

---

## ⚠️ 为什么没有用 GitHub Actions

最初配了 `.github/workflows/pages.yml`，推送时被拒：

```
refusing to allow a Personal Access Token to create or update workflow
`.github/workflows/pages.yml` without `workflow` scope
```

**`workflow` scope 意味着 token 可以修改 CI 流水线** —— 这是代码执行入口。
为一个纯静态站点要这个权限，风险收益不成比例。

**解决方案**：改为「分支直发 Pages」。

- `build_site.py` 直接产出静态 HTML，无需 npm / 构建器
- 仓库含 `.nojekyll`，GitHub 不会用 Jekyll 二次处理
- Pages 配置：`source = { branch: main, path: / }`，`build_type = legacy`
- **零 CI 依赖、零额外权限**

> 备用 Actions 工作流保留在 `deploy/pages-actions.yml`。
> 若要启用：给 token 加 `workflow` scope → 文件移回 `.github/workflows/pages.yml`
> → Settings → Pages 把 Source 改为 **GitHub Actions**。

---

## ⚠️ 实测发现：Fine-grained token 拿不到 star 明细

GitHub 的 stargazers 时间戳接口对 Fine-grained token 返回 **403**，
即使目标是**公开仓库**也一样：

```
GET /repos/{public_repo}/stargazers  (Accept: application/vnd.github.star+json)
→ 403 Resource not accessible by personal access token
```

所以「近 30 天 star 增量」这个指标在本账号的 token 权限下**拿不到**。

### 本项目的应对：势头分

常青榜改用综合「**势头分**」排序，全部信号来自可获取的数据
（见 `tools/collect.py` 的 `momentum_score()`）：

| 信号 | 权重 | 含义 |
|------|------|------|
| 近 90 天 commit 数 | ≤30 | 维护强度（log2 压缩，防刷提交碾压） |
| fork / star 比 | ≤25 | 真有人在动手用，而非只是收藏 |
| 最近提交新鲜度 | ≤20 | 是否还在活跃 |
| 推荐分 | ≤15 | 综合健康度（已含许可证、issue 压力） |
| 贡献者数 | ≤20 | 社区规模与广度 |

效果：榜单能区分「仍在高强度维护的老将」与「早已停滞的老面孔」，
不会退化成 star 总数的复制粘贴。

> 若未来想拿到真实 star 增速，需要 Classic PAT（`repo` 权限）—— 但那会显著
> 扩大权限范围，不推荐。可行替代是定期快照 star 总数做差分，或用第三方 star-history 服务。

---

## Token 安全模型

### 解析顺序

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | 环境变量 `GITHUB_TOKEN` | 临时使用，进程退出即失效 |
| 2 | `~/.config/qwenpaw/github_token` | **当前使用的位置**，权限 600 |
| 3 | `pages/.local-secrets/github_token.bak` | 兜底备份（已 gitignore） |

脚本**只把 token 塞进 HTTP header 或 credential helper 的 stdin**，
绝不 echo、绝不写入日志、绝不作为命令行参数（避免出现在 `ps` 进程列表）。

### 推送方式（`tools/push.sh`）

```sh
git -c credential.helper='!f() { echo username=x-access-token; echo "password=$GITHUB_TOKEN"; }; f' \
    push -u origin main
```

token 只在进程内存中流转：

- ❌ 不写入 `.git/config`
- ❌ 不出现在 remote URL
- ❌ 不落盘到 `~/.git-credentials`
- ✅ remote URL 始终是干净的 `https://github.com/zcoriander/zcoriander.github.io.git`

---

## 换 token 的最简流程（打不开终端也能做）

1. 在 GitHub 生成新 token（权限见上表）
2. 把 token 存成文件，放到工作区根目录，命名 `github_token`
3. 告诉 Agent「token 换好了」

Agent 会自动执行：

1. 校验格式（前缀 / 长度 / 字符集），**不打印内容**
2. `chmod 600` 收紧权限
3. 复制到 `~/.config/qwenpaw/github_token`
4. 从工作区移除原文件（移到 `.local-secrets/` 备份，不永久删除）
5. 加固 `.gitignore`
6. 用 `gh_api.sh --auth-only` 自检

---

## ❌ 绝对不要做的事

| 做法 | 为什么危险 |
|------|-----------|
| 把 token 粘贴到聊天窗口 | 进入对话历史、模型上下文、日志，永久留存 |
| 写进 `.env` 后提交到 Git | 即使是私有仓库也可能被误公开或被备份系统抓取 |
| 写进 `git remote` URL | `https://token@github.com/...` 会进入 `.git/config`，且可能被日志记录 |
| 用 Classic PAT + `repo` 全量权限 | 一次泄露 = 整个账号沦陷 |
| 授予 `Administration` 权限 | 能改仓库设置、删分支、删仓库 —— 本项目不需要 |
| token 文件权限设为 644 | 同机其他用户可读 |

---

## 想要更彻底？用 SSH Key 代替 token 推送

token 只用于读 API，推送走 SSH：

```bash
ssh-keygen -t ed25519 -C "zcoriander@github"
cat ~/.ssh/id_ed25519.pub
# 粘贴到 GitHub → Settings → SSH and GPG keys → New SSH key
```

---

## 泄露了怎么办

1. 立刻去 GitHub → Settings → Developer settings → Personal access tokens → **Revoke**
2. 检查授权记录：Settings → Developer settings → **Personal access tokens → your token → Recent usage**
3. 生成新 token 并按上面的流程重新配置
4. 如果怀疑账号被入侵，开启 2FA

---

## 日常自检命令

```bash
cd pages

# 认证状态（不显示 token）
sh tools/gh_api.sh --auth-only

# API 限额
sh tools/gh_api.sh GET rate_limit | python3 -m json.tool

# token 文件权限应为 -rw-------
stat -c '%A %s bytes' ~/.config/qwenpaw/github_token

# 确认工作区没有残留 token
git ls-files | grep -iE 'token|\.env$|secret' && echo '!!! 发现敏感文件 !!!' || echo 'OK'

# 确认 .git/config 和 remote URL 不含 token
git remote get-url origin | grep -qE 'github_pat_|ghp_' && echo '!!! !!!' || echo 'OK: URL 干净'
```

---

*相关文档：`README.md`（项目说明）· `docs/SECURITY.md`（本文）*
