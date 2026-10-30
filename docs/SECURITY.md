# 🔐 GitHub Token 安全接入指南

> 目标：**Token 永远不进入 LLM 上下文，不出现在聊天记录，不写进任何 Git 仓库。**

---

## ✅ 当前状态（已配置）

Token 已就位，**不在工作区内**，位于：

```
~/.config/qwenpaw/github_token    权限 600
```

验证命令（只输出状态，不显示 token）：

```bash
sh tools/gh_api.sh --auth-only
# → auth: token present (source: file:/root/.config/qwenpaw/github_token)
# → rate_limit_probe_http: 200
```

已确认：

- Token 类型：**Fine-grained PAT**（`github_pat_` 前缀）
- 认证身份：`zcoriander`（User）
- 可访问 `zcoriander.github.io`，具备 push / admin 权限
- API 限额：**5000 次/小时**（未认证仅 60 次/小时），搜索 **30 次/分钟**（未认证 10）

---

## ⚠️ 实测发现：Fine-grained token 拿不到 star 明细

GitHub 的 stargazers 时间戳接口对 Fine-grained token 返回：

```
403 Resource not accessible by personal access token
```

即使目标是**公开仓库**也一样。所以「近 30 天 star 增量」这个指标在本账号的 token 权限下**拿不到**。

**本项目的应对**（见 `tools/collect.py` 的 `momentum_score()`）：

常青榜改用「**势头分**」综合排序，信号全部来自认证后可得的数据：

| 信号 | 权重 | 含义 |
|------|------|------|
| 近 90 天 commit 数 | ≤40 | 维护强度（对数计分，防刷提交碾压） |
| fork / star 比 | ≤25 | 真有人在动手用，而非只是收藏 |
| 最近提交新鲜度 | ≤20 | 是否还在活跃 |
| 推荐分 | ≤15 | 综合健康度（已含许可证、issue 压力） |
| 贡献者数 | ≤10 | 社区规模与广度 |

效果：榜单能区分「仍在高强度维护的老将」与「早已停滞的老面孔」，不会退化成 star 总数的复制粘贴。

> 如果未来想拿到真实 star 增速，需要用 **Classic PAT**（`repo` 权限），但那会显著扩大权限范围 —— 不推荐。可行的替代是引入第三方 star-history 服务，或自行定期快照 star 总数做差分。

---

## Token 安全模型

### 解析顺序

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | 环境变量 `GITHUB_TOKEN` | 临时使用，进程退出即失效 |
| 2 | `~/.config/qwenpaw/github_token` | **当前使用的位置**，权限 600 |
| 3 | `pages/.local-secrets/github_token.bak` | 兜底备份（已 gitignore） |

脚本**只把 token 塞进 HTTP header**，绝不 echo、绝不写入日志、绝不作为命令行参数（避免出现在 `ps` 进程列表）。

### 如果需要更换 token

由于你打不开终端，最简单的方式是：

1. 直接把新 token 文件放到工作区根目录，命名为 `github_token`
2. 告诉 Agent「token 换好了」
3. Agent 会自动：校验格式 → 收紧权限到 600 → 迁移到 `~/.config/qwenpaw/` → 从工作区移除 → 加固 `.gitignore`

---

## ❌ 绝对不要做的事

| 做法 | 为什么危险 |
|------|-----------|
| 把 token 粘贴到聊天窗口 | 进入对话历史、模型上下文、日志，永久留存 |
| 写进 `.env` 后提交到 Git | 即使是私有仓库也可能被误公开或被备份系统抓取 |
| 写进 `git remote` URL | `https://token@github.com/...` 会进入 `.git/config`，且可能被日志记录 |
| 用 Classic PAT + `repo` 全量权限 | 一次泄露 = 整个账号沦陷 |
| 授予 `Administration` 权限 | 能改仓库设置、删分支、删仓库 —— 本项目完全不需要 |
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
sh tools/gh_api.sh --auth-only
sh tools/gh_api.sh GET rate_limit | python3 -m json.tool

# 确认 token 文件权限正确
stat -c '%A %s bytes' ~/.config/qwenpaw/github_token   # 应为 -rw-------

# 确认工作区没有残留 token
git ls-files | grep -iE 'token|\.env$|secret' && echo '!!! 发现敏感文件 !!!' || echo 'OK'
```

---

*相关文档：`README.md`（项目说明）· `docs/SECURITY.md`（本文）*

