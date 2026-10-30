#!/usr/bin/env python3
"""
collect.py — 从 GitHub API 收集项目，分类并打分，产出 data/projects.json。

分类策略（每类固定 10 条）：
  hot_week    近 30 天新建且 star 增长快
  new_star    3 个月内新建的黑马
  beginner    有 good-first-issue / beginner 标签
  fun         有 fun / experimental / creative 标签
  learning    有 tutorial / learning / education 标签
  evergreen   star 总量前列的老牌项目 —— 特殊处理：按近 30 天 star 增长排序

Token 处理：优先环境变量 GITHUB_TOKEN，其次 ~/.config/qwenpaw/github_token。
token 只出现在 HTTP header，永远不写入输出文件或日志。
"""
import json, os, sys, time, math, subprocess
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
API = "https://api.github.com"
UA = "qwenpaw-github-scout"
TOKEN_FILE = os.environ.get(
    "GITHUB_TOKEN_FILE", os.path.expanduser("~/.config/qwenpaw/github_token")
)

TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not TOKEN and os.path.isfile(TOKEN_FILE):
    try:
        with open(TOKEN_FILE) as f:
            TOKEN = f.read().strip()
    except OSError:
        pass

# 兜底：若标准位置没有，尝试工作区 .local-secrets/ 下的备份
if not TOKEN:
    _fallback = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".local-secrets", "github_token.bak",
    )
    if os.path.isfile(_fallback):
        try:
            with open(_fallback) as f:
                TOKEN = f.read().strip()
            TOKEN_FILE = _fallback
        except OSError:
            pass

# token 通过 curl 的 header 传入，绝不出现在 argv（避免 ps 泄漏），也绝不打印
_AUTH_HEADER = f"Authorization: Bearer {TOKEN}" if TOKEN else ""


def get(path, retries=3, accept="application/vnd.github+json"):
    """GET GitHub API，返回 (json, body_text)。使用 curl 以兼容代理环境。"""
    url = f"{API}/{path}" if not path.startswith("http") else path
    for attempt in range(retries):
        cmd = ["curl", "-s", "--max-time", "40",
               "-H", f"Accept: {accept}",
               "-H", f"User-Agent: {UA}"]
        if _AUTH_HEADER:
            cmd += ["-H", _AUTH_HEADER]
        cmd.append(url)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=50)
            body = r.stdout
        except subprocess.TimeoutExpired:
            body = ""
        if body:
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = None
            if isinstance(data, dict) and data.get("message"):
                msg = data["message"]
                if "rate limit" in msg.lower() or "abuse" in msg.lower():
                    if attempt < retries - 1:
                        wait = 30 if "secondary" in msg.lower() else 70
                        print(f"    ! rate limited, waiting {wait}s", file=sys.stderr)
                        time.sleep(wait)
                        continue
                if "Not Found" in msg:
                    return None, ""
            if data is not None:
                return data, body
        if attempt < retries - 1:
            time.sleep(4)
            continue
        print(f"    ! failed: {path}", file=sys.stderr)
    return None, ""


def search(q, sort="stars", per_page=30):
    """搜索仓库，返回精简列表"""
    import urllib.parse
    params = urllib.parse.urlencode(
        {"q": q, "sort": sort, "order": "desc", "per_page": per_page}
    )
    data, _ = get(f"search/repositories?{params}")
    if not data or "items" not in data:
        return []
    out = []
    for r in data["items"]:
        out.append(
            {
                "full_name": r["full_name"],
                "url": r["html_url"],
                "description": r["description"],
                "language": r["language"],
                "stars": r["stargazers_count"],
                "forks": r["forks_count"],
                "open_issues": r["open_issues_count"],
                "topics": r.get("topics", []),
                "created_at": r["created_at"],
                "pushed_at": r["pushed_at"],
                "license": (r.get("license") or {}).get("spdx_id"),
                "owner": r["owner"]["login"],
                "name": r["name"],
            }
        )
    return out


def stargazers_timestamps(repo, total_stars):
    """
    取该仓库最近 star 的时间戳。
    stargazers 接口按时间**升序**返回，最新的在最后一页。
    需要特殊 Accept header: application/vnd.github.star+json 才带 starred_at。
    采最后 2 页（最多 200 个最新 star），足以判断 30 天窗口。
    """
    if total_stars < 100:
        return []
    last_page = max(1, (total_stars + 99) // 100)
    stamps = []
    for page in range(last_page, max(0, last_page - 2), -1):
        data, _ = get(
            f"repos/{repo}/stargazers?per_page=100&page={page}",
            accept="application/vnd.github.star+json",
            retries=2,
        )
        if not data or not isinstance(data, list) or not data:
            continue
        got_ts = False
        for s in data:
            if isinstance(s, dict) and "starred_at" in s:
                stamps.append(s["starred_at"])
                got_ts = True
            else:
                break
        if not got_ts:
            break
        time.sleep(0.3)
    return stamps


def commits_since(repo, since_iso):
    """
    统计某时间点以来的 commit 数（利用 Link header 的 rel="last" 页码）。
    这是免认证可得的活跃度信号 —— stargazers 时间戳接口需要认证才能用，
    所以未配置 token 时用它作为增速的替代指标。
    """
    cmd = ["curl", "-s", "-i", "--max-time", "40",
           "-H", "Accept: application/vnd.github+json",
           "-H", f"User-Agent: {UA}"]
    if _AUTH_HEADER:
        cmd += ["-H", _AUTH_HEADER]
    cmd.append(f"{API}/repos/{repo}/commits?since={since_iso}&per_page=1")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=50)
    except subprocess.TimeoutExpired:
        return None
    import re
    m = re.search(r'[?&]page=(\d+)>; rel="last"', r.stdout)
    if m:
        return int(m.group(1))
    # 没有 Link header 说明不足 1 页，即 0 或 1 条
    body = r.stdout.split("\r\n\r\n", 1)[-1]
    try:
        data = json.loads(body)
        return len(data) if isinstance(data, list) else 0
    except Exception:
        return None


def momentum_score(p):
    """
    「势头分」—— 常青榜的核心排序指标。

    背景：GitHub 的 stargazers 时间戳接口对 fine-grained token 返回
    403（Resource not accessible by personal access token），即使仓库公开也拿不到。
    所以无法直接计算「近 30 天 star 增量」。

    替代方案：组合多个认证后可得、且能反映「上升势头」的信号：
      1. 近 90 天 commit 数    —— 维护强度（对数计分，防止刷提交碾压）
      2. fork/star 比          —— 真有人在动手用的比例
      3. 最近提交新鲜度        —— 是否还在活跃
      4. 推荐分                —— 综合健康度（已含许可证、issue 压力等）
      5. 社区贡献者数          —— 社区规模与广度

    这几个信号叠加，能有效区分「还在高强度维护的老将」和「早已停滞的老面孔」，
    让常青榜不会退化成 star 总数的复制粘贴。
    """
    import math as _m

    score = 0.0

    # 1) 维护强度（最多 30 分）—— 用 log2 压缩，比 log10 更有区分度
    c = p.get("commits_90d")
    if c is not None:
        import math as _m
        score += min(30, _m.log2(max(c, 1)) * 2.6)

    # 2) fork/star 比（最多 25 分）—— fork = 真打算动手用
    stars = max(p.get("stars", 1), 1)
    ratio = p.get("forks", 0) / stars
    score += min(25, ratio * 420)

    # 3) 最近提交新鲜度（最多 20 分）
    ds = days_since(p.get("pushed_at", ""))
    if ds <= 7:
        score += 20
    elif ds <= 14:
        score += 16
    elif ds <= 30:
        score += 12
    elif ds <= 90:
        score += 7
    elif ds <= 180:
        score += 3

    # 4) 推荐分（最多 15 分）
    score += p.get("score", 0) * 0.15

    # 5) 社区贡献者数（最多 20 分）—— log2，区分度更好
    contrib = p.get("contributors")
    if contrib is not None:
        import math as _m
        score += min(20, _m.log2(max(contrib, 1)) * 2.2)

    return round(score, 1)


def contributors_count(repo):
    """贡献者数（用 Link header 的 rel="last" 页码，per_page=1 时即总数）"""
    cmd = ["curl", "-s", "-i", "--max-time", "40",
           "-H", "Accept: application/vnd.github+json",
           "-H", f"User-Agent: {UA}"]
    if _AUTH_HEADER:
        cmd += ["-H", _AUTH_HEADER]
    cmd.append(f"{API}/repos/{repo}/contributors?per_page=1&anon=1")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=50)
    except subprocess.TimeoutExpired:
        return None
    import re
    m = re.search(r'[?&]page=(\d+)>; rel="last"', r.stdout)
    if m:
        return int(m.group(1))
    return None


def estimate_growth(repo, total_stars):
    """
    估算近 30 天 star 增长。
    stargazers 时间戳接口需要认证，未配置 token 时返回 None。
    """
    stamps = stargazers_timestamps(repo, total_stars)
    if not stamps:
        return None

    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat().replace(
        "+00:00", "Z"
    )
    in_window = sum(1 for s in stamps if s >= cutoff)
    sample = len(stamps)

    if sample == 0:
        return None
    if in_window == sample:
        return int(min(total_stars, sample))
    est = (in_window / sample) * total_stars
    return int(min(total_stars, max(in_window, est)))


def days_since(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return max(0, (datetime.now(timezone.utc) - dt).days)
    except Exception:
        return 9999


def score_repo(p):
    """推荐分 0-100：star 规模 + 活跃度 + 健康度 + 文档友好度"""
    stars = p.get("stars", 0)
    s = 0
    # star 规模（对数，最多 40 分）
    s += min(40, math.log10(max(stars, 1)) * 10)
    # 最近提交活跃度（最多 25 分）
    ds = days_since(p.get("pushed_at", ""))
    if ds <= 7:
        s += 25
    elif ds <= 14:
        s += 20
    elif ds <= 30:
        s += 15
    elif ds <= 90:
        s += 8
    elif ds <= 365:
        s += 3
    # fork/star 比例健康度（最多 15 分）—— fork 说明有人真的动手用
    ratio = p.get("forks", 0) / max(stars, 1)
    if ratio >= 0.15:
        s += 15
    elif ratio >= 0.08:
        s += 12
    elif ratio >= 0.04:
        s += 8
    elif ratio >= 0.02:
        s += 5
    else:
        s += 2
    # 许可证（最多 10 分）
    lic = p.get("license")
    if lic and lic not in ("NOASSERTION", "Other"):
        s += 10
    elif lic:
        s += 5
    # issue 响应压力惩罚（最多扣 10 分）
    oi = p.get("open_issues", 0)
    if oi > 2000 and stars < 20000:
        s -= 6
    elif oi > 800:
        s -= 3
    return round(min(100, max(0, s)), 1)


def dedupe(items):
    seen, out = set(), []
    for it in items:
        if it["full_name"] in seen:
            continue
        seen.add(it["full_name"])
        out.append(it)
    return out


def load_curated_names():
    """读取 enrich.py 里人工撰写文案的项目名单"""
    path = os.path.join(ROOT, "tools", "enrich.py")
    names = []
    try:
        with open(path, encoding="utf-8") as f:
            src = f.read()
        # 解析 DEEP_CONTENT 字典的 key
        import re
        block = re.search(r"DEEP_CONTENT\s*=\s*\{(.*?)\n\}", src, re.S)
        if block:
            names = re.findall(r'^\s*"([^"]+)"\s*:\s*\{', block.group(1), re.M)
    except OSError:
        pass
    return names


def fetch_repo_detail(full_name):
    """拉取单个仓库的详情（用于人工文案项目未出现在当前榜单时）"""
    data, _ = get(f"repos/{full_name}")
    if not data or "full_name" not in data:
        return None
    return {
        "full_name": data["full_name"],
        "url": data["html_url"],
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "open_issues": data.get("open_issues_count", 0),
        "topics": data.get("topics", []),
        "created_at": data.get("created_at", ""),
        "pushed_at": data.get("pushed_at", ""),
        "license": (data.get("license") or {}).get("spdx_id"),
        "owner": data.get("owner", {}).get("login", ""),
        "name": data.get("name", ""),
    }


def pick(items, n=10, exclude=()):
    """打分排序后取前 n"""
    ex = set(exclude)
    pool = [i for i in items if i["full_name"] not in ex]
    for p in pool:
        p["score"] = score_repo(p)
    pool.sort(key=lambda x: x["score"], reverse=True)
    return pool[:n]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"认证状态: {'已配置 token' if TOKEN else '未认证（受限流影响）'}")

    today = datetime.now(timezone.utc)
    d30 = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    d90 = (today - timedelta(days=90)).strftime("%Y-%m-%d")
    d365 = (today - timedelta(days=365)).strftime("%Y-%m-%d")

    print("\n[1/6] 抓取 hot_week (近30天新建)...")
    hot = search(f"created:>{d30} stars:>150", per_page=40)

    print("[2/6] 抓取 new_star (近90天新建)...")
    new = search(f"created:>{d90} stars:>200", per_page=40)

    print("[3/6] 抓取 beginner...")
    beginner = []
    for q in ["topic:beginner", "topic:good-first-issue",
              "topic:first-timers-only", "topic:beginner-friendly"]:
        beginner += search(q, per_page=25)
        time.sleep(2)
    beginner = dedupe(beginner)

    print("[4/6] 抓取 fun / creative...")
    fun = []
    for q in ["topic:fun", "topic:creative", "topic:experimental",
              "topic:showcase", "topic:awesome-project"]:
        fun += search(q, per_page=25)
        time.sleep(2)
    fun = dedupe(fun)

    print("[5/6] 抓取 learning...")
    learning = []
    for q in ["topic:tutorial", "topic:learning", "topic:education",
              "topic:awesome", "topic:course", "topic:roadmap"]:
        learning += search(q, per_page=25)
        time.sleep(2)
    learning = dedupe(learning)

    print("[6/6] 抓取 evergreen (star 总量前列)...")
    evergreen_raw = []
    for q in ["stars:>80000", "stars:>50000"]:
        evergreen_raw += search(q, per_page=30)
        time.sleep(2)
    evergreen_raw = dedupe(evergreen_raw)

    # 常青榜特殊处理：
    # star 总量榜几乎年年不变（老项目增速趋近于零），
    # 所以改用「近 30 天 star 增长」排序 —— 看谁在悄悄上位。
    print("    正在估算各分类的 star 增速（用于常青榜重排）...")

    categories = {}
    used = set()

    # hot_week
    hot = [h for h in hot if days_since(h["created_at"]) <= 30]
    categories["hot_week"] = pick(hot, 10)
    used |= {p["full_name"] for p in categories["hot_week"]}

    # new_star：排除已进 hot_week 的
    new = [n for n in new if days_since(n["created_at"]) <= 90]
    categories["new_star"] = pick(new, 10, exclude=used)
    used |= {p["full_name"] for p in categories["new_star"]}

    # beginner
    categories["beginner"] = pick(beginner, 10, exclude=used)
    used |= {p["full_name"] for p in categories["beginner"]}

    # fun
    categories["fun"] = pick(fun, 10, exclude=used)
    used |= {p["full_name"] for p in categories["fun"]}

    # learning
    categories["learning"] = pick(learning, 10, exclude=used)
    used |= {p["full_name"] for p in categories["learning"]}

    # 常青榜特殊处理：
    # star 总量榜几乎年年不变（老项目增速趋近于零），
    # 所以不按 star 总数排，而是算「势头分」——组合维护强度、fork/star 比、
    # 提交新鲜度、推荐分、贡献者数。详见 momentum_score() 的说明。
    evergreen_pool = [e for e in evergreen_raw if e["full_name"] not in used]
    since90 = (today - timedelta(days=90)).isoformat().replace("+00:00", "Z")
    print(f"    为 {len(evergreen_pool[:20])} 个候选计算势头信号...")
    for i, e in enumerate(evergreen_pool[:20], 1):
        e.setdefault("score", score_repo(e))
        c = commits_since(e["full_name"], since90)
        if c is not None:
            e["commits_90d"] = c
        ct = contributors_count(e["full_name"])
        if ct is not None:
            e["contributors"] = ct
        print(f"    [{i}/20] {e['full_name']}: commits90={e.get('commits_90d')} "
              f"contributors={e.get('contributors')} score={e.get('score')}")
        time.sleep(0.35)

    for p in evergreen_pool:
        p["momentum"] = momentum_score(p)

    # 势头分优先；同分再按 star 数
    evergreen_pool.sort(key=lambda x: (x.get("momentum", 0), x.get("stars", 0)), reverse=True)
    evergreen = evergreen_pool[:10]
    for p in evergreen:
        p["score"] = score_repo(p)
    categories["evergreen"] = evergreen[:10]

    # 标注
    for p in categories["hot_week"]:
        p["note"] = f"建于 {p['created_at'][:10]}，{days_since(p['created_at'])} 天"
    for p in categories["new_star"]:
        p["note"] = f"建于 {p['created_at'][:10]}，{days_since(p['created_at'])} 天，冲劲十足"
    for p in categories["beginner"]:
        p["note"] = "适合作为第一份开源贡献"
    for p in categories["fun"]:
        p["note"] = "有意思，逛着逛着就学会了"
    for p in categories["learning"]:
        p["note"] = "系统学习路径"
    for p in categories["evergreen"]:
        m = p.get("momentum")
        bits = []
        if p.get("commits_90d") is not None:
            bits.append(f"近 90 天 {p['commits_90d']} 次提交")
        if p.get("contributors") is not None:
            bits.append(f"{p['contributors']} 位贡献者")
        if bits:
            p["note"] = " · ".join(bits) + " —— 势头分 " + str(m)
            p["badge"] = "📈 势头榜"
            p["growth_note"] = f"势头 {m}"
        else:
            p["note"] = f"star 总量 {p['stars']}，势头分 {m}"
            p["badge"] = "🏛️ 常青"
            p["growth_note"] = f"势头 {m}"

    # 深挖：优先挑选「我写过人工文案」的项目，再从各分类补足
    # （人工文案清单由 enrich.py 维护，这里读取以确保这些项目一定被收录）
    curated = load_curated_names()
    deep = []
    seen_deep = set()
    by_name = {}
    for cid, items in categories.items():
        for p in items:
            by_name[p["full_name"]] = p

    def make_deep(p, cid):
        if p.get("growth_30d") is None and p["stars"] > 100000:
            g = estimate_growth(p["full_name"], p["stars"])
            if g is not None:
                p["growth_30d"] = g
        return {
            "name": p["full_name"],
            "url": p["url"],
            "category": cid,
            "language": p.get("language"),
            "stars": p.get("stars", 0),
            "growth_30d": p.get("growth_30d"),
            "summary": p.get("description") or "",
            "topics": p.get("topics", [])[:8],
            "score": p.get("score"),
            "license": p.get("license"),
            "forks": p.get("forks", 0),
            "open_issues": p.get("open_issues", 0),
            "pushed_at": p.get("pushed_at", "")[:10],
        }

    # 1) 人工文案项目优先
    for name in curated:
        p = by_name.get(name)
        if p is None:
            # 不在当前榜单里，单独拉取详情
            p = fetch_repo_detail(name)
            if p:
                p["score"] = score_repo(p)
                by_name[name] = p
                cid = "curated"
                categories.setdefault("curated", []).append(p)
        else:
            cid = next(
                (c for c, items in categories.items()
                 if any(i["full_name"] == name for i in items)),
                "curated",
            )
        if p:
            deep.append(make_deep(p, cid))
            seen_deep.add(name)

    # 2) 从各分类补足到 12 个
    for cid in ["hot_week", "evergreen", "beginner", "fun", "learning", "new_star"]:
        for p in categories.get(cid, []):
            if len(deep) >= 12:
                break
            if p["full_name"] in seen_deep:
                continue
            seen_deep.add(p["full_name"])
            deep.append(make_deep(p, cid))
        if len(deep) >= 12:
            break

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "categories": categories,
        "deep_dives": deep,
        "hero_picks": [],
        "thoughts": [],
        "category_notes": {
            "evergreen": "这一栏不看 star 总数（老牌项目几乎不涨，总数永远那几个），改看近 30 天新增 star——谁在悄悄上位，一眼就能看出来。",
        },
    }

    with open(os.path.join(DATA_DIR, "projects.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("\n完成:")
    for cid, items in categories.items():
        print(f"  {cid}: {len(items)} 个")
    print(f"  deep_dives: {len(deep)} 个")


if __name__ == "__main__":
    main()
