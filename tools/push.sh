#!/bin/sh
# push.sh — 安全推送脚本
#
# token 处理原则：
#   - 从 ~/.config/qwenpaw/github_token 读入 shell 变量（仅存在于进程内存）
#   - 通过 git credential helper 的 stdin/stdout 传递，token 不会：
#       · 写入 .git/config
#       · 出现在 remote URL
#       · 落盘到 ~/.git-credentials 等凭据文件
#       · 出现在 ps 进程列表（不作为 argv 传递）
#   - 脚本结束时 unset
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
export GITHUB_TOKEN

echo "→ 推送分支: $BRANCH"
echo "→ 认证方式: 内存态 credential helper（token 不落盘）"

# credential helper 通过 stdin 接收协议/主机，通过 stdout 返回凭据。
# token 只在进程内存中流转，不写入任何磁盘文件。
HELPER='!f() { echo username=x-access-token; echo "password=$GITHUB_TOKEN"; }; f'

git -c credential.helper="$HELPER" push -u origin "$BRANCH"

unset GITHUB_TOKEN
echo "✓ 推送完成"
