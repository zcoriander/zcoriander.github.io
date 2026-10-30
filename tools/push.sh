#!/bin/sh
# push.sh — 安全推送脚本
#
# token 处理原则：
#   - 从 ~/.config/qwenpaw/github_token 读入 shell 变量（内存）
#   - 通过 git -c http.extraheader 传递，token 只存在于进程内存
#   - 不写入 .git/config、不出现在 remote URL、不落盘到任何文件
#   - 脚本结束后 unset
#
# 用法：sh tools/push.sh [branch]

set -e

TOKEN_FILE="${GITHUB_TOKEN_FILE:-$HOME/.config/qwenpaw/github_token}"
BRANCH="${1:-main}"

if [ ! -r "$TOKEN_FILE" ]; then
  echo "✗ 未找到 token 文件: $TOKEN_FILE" >&2
  echo "  请把 token 放到该路径，或设置 GITHUB_TOKEN_FILE 环境变量" >&2
  exit 1
fi

GITHUB_TOKEN="$(tr -d '\r\n' < "$TOKEN_FILE")"
if [ -z "$GITHUB_TOKEN" ]; then
  echo "✗ token 文件为空: $TOKEN_FILE" >&2
  exit 1
fi

echo "→ 推送分支: $BRANCH"
echo "→ 认证方式: http.extraheader（token 不落盘）"

# http.extraheader 让 git 用 Authorization 头认证，
# 而不是把 token 写进 remote URL 或 .git/config
git -c "http.https://github.com/.extraheader=Authorization: Bearer ${GITHUB_TOKEN}" \
    push -u origin "$BRANCH"

unset GITHUB_TOKEN
echo "✓ 推送完成"
