# 🔐 GitHub Token 安全接入指南

> 目标：**Token 永远不进入 LLM 上下文，不出现在聊天记录，不写进任何 Git 仓库。**

---

## 推荐方案：环境变量 + 文件兜底

本项目已内置 `tools/gh_api.sh`，它按以下顺序解析 token：

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | 环境变量 `GITHUB_TOKEN` | 临时使用，进程退出即失效 |
| 2 | 文件 `$GITHUB_TOKEN_FILE` | 默认 `~/.config/qwenpaw/github_token` |

脚本**只把 token 塞进 HTTP header**，绝不 echo、绝不写入日志、绝不作为命令行参数（避免出现在 `ps` 进程列表）。

---

## 你需要做的三步

### 第 1 步：生成 Fine-grained Token

GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token

**权限设置（按需最小化）：**

| Repository | Permissions | 级别 | 用途 |
|------------|-------------|------|------|
| `zcoriander.github.io` | Contents | Read and write | 推送 Pages 站点内容 |
| `zcoriander.github.io` | Pages | Read and write | 触发/管理 Pages 部署 |
| 公开仓库 | Metadata | Read-only | 查询项目元信息、star 数 |

- **Resource owner**：`zcoriander`（只选你自己的账号）
- **Repository access**：`Only select repositories` → 仅勾选 `zcoriander.github.io`
- **Expiration**：建议 90 天，到期前提醒自己轮换

> ⚠️ 不要勾选 `Administration`。它能改仓库设置、删分支、删仓库——我们完全不需要。

### 第 2 步：把 token 存到本地文件（推荐）

在你自己的终端执行：

```bash
mkdir -p ~/.config/qwenpaw
read -rs -p "粘贴 GitHub Token: " TOKEN && echo
printf '%s' "$TOKEN" | tr -d '\r\n' > ~/.config/qwenpaw/github_token
chmod 600 ~/.config/qwenpaw/github_token
unset TOKEN
```

验证：

```bash
cat ~/.config/qwenpaw/github_token | wc -c   # 应输出一个 40~255 的数字
```

### 第 3 步：告诉 Agent 位置（不是 token 内容）

只需要说：**"token 已存到默认位置"** 或 **"用环境变量 GITHUB_TOKEN"**。

Agent 会用 `tools/gh_api.sh --auth-only` 自检，它只输出 `auth: token present` 和一个 HTTP 状态码，**不会显示 token 本身**。

---

## 一次性环境变量方式（更短暂，更安全）

如果只是想临时用：

```bash
export GITHUB_TOKEN="$(cat ~/.config/qwenpaw/github_token)"
# ... 让 Agent 执行操作 ...
unset GITHUB_TOKEN
```

---

## ❌ 绝对不要做的事

| 做法 | 为什么危险 |
|------|-----------|
| 把 token 粘贴到聊天窗口 | 进入对话历史、模型上下文、日志，永久留存 |
| 写进 `.env` 后提交到 Git | 即使是私有仓库也可能被误公开或被备份系统抓取 |
| 写进 `git remote` URL | `https://token@github.com/...` 会进入 `.git/config`，且可能被日志记录 |
| 用 Classic PAT + `repo` 全量权限 | 一次泄露 = 整个账号沦陷 |
| 给我一个 admin 权限 token | 我不需要这个权限，也不应该持有它 |

---

## 想要更安全？用 SSH Key 代替 token 推送

如果你不想让 token 参与推送，用 SSH 更彻底：

```bash
ssh-keygen -t ed25519 -C "zcoriander@github"
cat ~/.ssh/id_ed25519.pub
# 粘贴到 GitHub → Settings → SSH and GPG keys → New SSH key
```

之后所有 `git push` 都不需要 token。token 只用于读 API。

---

## 泄露了怎么办

1. 立刻去 GitHub → Settings → Developer settings → Personal access tokens → **Revoke**
2. 检查该 token 的授权记录：Settings → Developer settings → **Personal access tokens → your token → Recent usage**
3. 生成新 token 并重复上面步骤
4. 如果怀疑账号被入侵，开启 2FA

---

## 日常自检命令

```bash
cd /path/to/pages
sh tools/gh_api.sh --auth-only
sh tools/gh_api.sh GET rate_limit | python3 -m json.tool
```

---

*相关文档：`docs/SECURITY.md`（策略说明）· `README.md`（项目说明）*
