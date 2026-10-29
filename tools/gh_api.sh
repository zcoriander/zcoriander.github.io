#!/bin/sh
# gh_api.sh — GitHub API helper that NEVER exposes the token to the LLM.
#
# Token resolution order:
#   1. $GITHUB_TOKEN (env)
#   2. $GITHUB_TOKEN_FILE (default: ~/.config/qwenpaw/github_token)
#
# The token value is never echoed, never logged, never passed as an argv value
# that would show up in `ps`. It is injected as a curl header only.
#
# Usage:
#   gh_api.sh GET "repos/{owner}/{repo}"
#   gh_api.sh GET "search/repositories?q=stars:%3E1000&per_page=10"
#   gh_api.sh --raw GET "path" > out.json      # headers included (for Link parsing)
#   gh_api.sh --auth-only                     # print only auth state, no token

set -e

TOKEN_FILE="${GITHUB_TOKEN_FILE:-$HOME/.config/qwenpaw/github_token}"

resolve_token() {
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    printf '%s' "$GITHUB_TOKEN"
  elif [ -r "$TOKEN_FILE" ]; then
    tr -d '\r\n' < "$TOKEN_FILE"
  else
    printf ''
  fi
}

TOKEN="$(resolve_token)"

if [ "$1" = "--auth-only" ]; then
  if [ -n "$TOKEN" ]; then
    echo "auth: token present (source: ${GITHUB_TOKEN:+env}${GITHUB_TOKEN:-file:$TOKEN_FILE})"
    code=$(curl -s -o /dev/null -w '%{http_code}' \
      -H "Authorization: Bearer $TOKEN" \
      -H "Accept: application/vnd.github+json" \
      -H "User-Agent: qwenpaw-gh" \
      https://api.github.com/rate_limit)
    echo "rate_limit_probe_http: $code"
  else
    echo "auth: NO TOKEN (unauthenticated mode)"
  fi
  exit 0
fi

MODE="normal"
if [ "$1" = "--raw" ]; then MODE="raw"; shift; fi

METHOD="$1"; PATH_="$2"; shift 2 || true

if [ "$MODE" = "raw" ]; then
  # include headers so we can parse Link rel="last"
  if [ -n "$TOKEN" ]; then
    curl -s -i -H "Authorization: Bearer $TOKEN" \
      -H "Accept: application/vnd.github+json" \
      -H "User-Agent: qwenpaw-gh" \
      "https://api.github.com/$PATH_"
  else
    curl -s -i -H "Accept: application/vnd.github+json" \
      -H "User-Agent: qwenpaw-gh" \
      "https://api.github.com/$PATH_"
  fi
else
  if [ -n "$TOKEN" ]; then
    curl -s -H "Authorization: Bearer $TOKEN" \
      -H "Accept: application/vnd.github+json" \
      -H "User-Agent: qwenpaw-gh" \
      "https://api.github.com/$PATH_"
  else
    curl -s -H "Accept: application/vnd.github+json" \
      -H "User-Agent: qwenpaw-gh" \
      "https://api.github.com/$PATH_"
  fi
fi
