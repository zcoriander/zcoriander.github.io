#!/usr/bin/env python3
"""
build_site.py — 从 data/projects.json / data/short_notes.json / data/deep_dives.json
生成 GitHub Pages 静态站点。

数据分层：
- data/projects.json        事实层：分类榜单、hero、分类备注、手记
- data/short_notes.json     判断层（短评）：65 条 one_line/for_who/hook，key=full_name
- data/deep_dives.json      判断层（深度拆解）：12 篇 A 标准详情，独立文件

设计原则：
- 纯静态、零构建依赖、无需 Node
- deep-dive.html 做索引页：全部短评 + 12 篇深度链接；每篇详情单独页面 deep-dive/{owner}_{repo}.html
- 新增 growth.html 成长档案页
"""
import json, os, html, datetime, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
PROJECTS = os.path.join(DATA, "projects.json")
SHORT_NOTES = os.path.join(DATA, "short_notes.json")
DEEP_DIVES = os.path.join(DATA, "deep_dives.json")
OUT = ROOT
DEEP_OUT = os.path.join(OUT, "deep-dive")

CATEGORIES = [
    ("hot_week",   "🔥 本周最热",   "新鲜上架，增速最快的一批"),
    ("new_star",   "🌱 黑马新星",   "三个月内冒头，冲劲十足"),
    ("beginner",   "🛠️ 新手友好",   "文档齐全、门槛低，第一份贡献从这里开始"),
    ("fun",        "💡 奇思妙想",   "脑洞和好玩，逛着逛着就学会了"),
    ("learning",   "📚 学习资源",   "系统学习路径，照着走不迷路"),
    ("evergreen",  "🏛️ 常青经典",   "星标王座变动不大，我们用增速来看新秩序"),
    ("curated",    "⭐ 精选收藏",   "个人反复打开、值得留下的项目"),
]

DEEP_ORDER = [
    "openclaw/openclaw",
    "obra/superpowers",
    "mattpocock/skills",
    "shareAI-lab/learn-claude-code",
    "ssloy/tinyrenderer",
    "codecrafters-io/build-your-own-x",
    "donnemartin/system-design-primer",
    "freeCodeCamp/freeCodeCamp",
    "firstcontributions/first-contributions",
    "seedds/nxnative",
    "storytold/effectcraft",
    "simbasjungles/free-my-tv",
]


def esc(s):
    return html.escape(s or "", quote=True)


def fmt(n):
    if n is None:
        return "—"
    if n >= 1000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    return str(n)


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def parse_repo(full_name):
    return full_name.split("/")[-1]


def deep_slug(full_name):
    return full_name.replace("/", "__")


def render_card(p, featured=False):
    """单张项目卡片（用于分类榜单）。"""
    growth = p.get("growth_30d")
    growth_html = ""
    if growth is not None:
        cls = "growth-hot" if growth >= 800 else ("growth-warm" if growth >= 300 else "growth-calm")
        growth_html = f'<span class="growth {cls}">+{fmt(growth)} /30d</span>'
    elif p.get("growth_note"):
        growth_html = f'<span class="growth growth-na">{esc(p["growth_note"])}</span>'

    lang = p.get("language")
    lang_html = f'<span class="lang">{esc(lang)}</span>' if lang else ""

    topics = "".join(
        f'<span class="topic">{esc(t)}</span>' for t in (p.get("topics") or [])[:5]
    )

    desc = p.get("description") or "（该项目没有写简介）"
    if len(desc) > 130:
        desc = desc[:130].rstrip() + "…"

    badge = ""
    if p.get("badge"):
        badge = f'<span class="badge">{esc(p["badge"])}</span>'

    score = ""
    if p.get("score") is not None:
        score = f'<span class="score">★ {p["score"]}</span>'

    return f"""      <article class="card{' featured' if featured else ''}" data-cat="{esc(p.get("category",""))}">
        <header class="card-head">
          <a class="repo" href="{esc(p["url"])}" target="_blank" rel="noopener">
            {esc(p["full_name"])}
          </a>
          {badge}
        </header>
        <p class="desc">{esc(desc)}</p>
        <div class="meta">
          <span class="stars">★ {fmt(p.get("stars",0))}</span>
          {growth_html}
          {score}
          {lang_html}
        </div>
        <div class="topics">{topics}</div>
        {f'<p class="note">{esc(p["note"])}</p>' if p.get("note") else ''}
      </article>"""


def render_short_note(full_name, note):
    """一条短评卡片（short_notes.json）。"""
    return f"""      <article class="note-card">
        <header class="note-head">
          <a class="repo" href="https://github.com/{esc(full_name)}" target="_blank" rel="noopener">
            {esc(full_name)}
          </a>
        </header>
        <p class="one-line">{esc(note.get("one_line",""))}</p>
        {f'<p class="for-who"><strong>适合：</strong>{esc(note.get("for_who",""))}</p>' if note.get("for_who") else ''}
        {f'<p class="hook"><strong>钩子：</strong>{esc(note.get("hook",""))}</p>' if note.get("hook") else ''}
      </article>"""


def render_deep_card(d):
    """深度拆解索引页上的单篇卡片。"""
    tags = "".join(f'<span class="topic">{esc(t)}</span>' for t in (d.get("tags") or []))
    return f"""      <article class="deep-card">
        <header class="deep-head">
          <h3><a href="deep-dive/{deep_slug(d['name'])}.html" class="deep-title">{esc(d["name"])}</a></h3>
          <div class="deep-meta">
            <span class="stars">★ {fmt(d.get("stars",0))}</span>
            {f'<span class="lang">{esc(d.get("language",""))}</span>' if d.get("language") else ''}
          </div>
        </header>
        <p class="deep-sub">{esc(d.get("summary",""))[:220]}{'…' if len(d.get("summary",""))>220 else ''}</p>
        <div class="deep-topics">{tags}</div>
        <p class="deep-verdict-preview">{esc(d.get("verdict",""))[:160]}{'…' if len(d.get("verdict",""))>160 else ''}</p>
        <a href="deep-dive/{deep_slug(d['name'])}.html" class="deep-link">阅读完整拆解 →</a>
      </article>"""


def render_deep_detail(d, all_deep):
    """单篇深度拆解独立页面 deep-dive/{owner}_{repo}.html。"""
    tags = "".join(f'<span class="topic">{esc(t)}</span>' for t in (d.get("tags") or []))
    sections = []
    for s in d.get("sections", []):
        body = "\n".join(f"<p>{esc(p)}</p>" for p in s.get("paragraphs", []))
        bullets = ""
        if s.get("bullets"):
            bullets = "<ul>" + "".join(f"<li>{esc(b)}</li>" for b in s["bullets"]) + "</ul>"
        sections.append(f"""        <h3>{esc(s["title"])}</h3>
        {body}
        {bullets}""")
    sections_joined = "\n".join(sections)
    metrics = ""
    if d.get("metrics"):
        metrics = '<div class="metrics">' + "".join(
            f'<div class="metric"><strong>{esc(m[0])}</strong><span>{esc(m[1])}</span></div>'
            for m in d["metrics"]
        ) + "</div>"
    # 上下篇链接（独立页已在 deep-dive/ 目录下，链接不应再带 deep-dive/ 前缀）
    idx = next((i for i, x in enumerate(all_deep) if x.get("name") == d.get("name")), -1)
    prev_html = next_html = ""
    if idx > 0:
        pd = all_deep[idx-1]
        prev_html = f'<a href="{deep_slug(pd["name"])}.html" class="nav-link prev">← {esc(pd["name"])}</a>'
    if idx >= 0 and idx < len(all_deep) - 1:
        nd = all_deep[idx+1]
        next_html = f'<a href="{deep_slug(nd["name"])}.html" class="nav-link next">{esc(nd["name"])} →</a>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>深度拆解：{esc(d["name"])} · GitHub 冲浪手记</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="../index.html"><span class="brand-mark">🌊</span><span>GitHub 冲浪手记</span></a>
    <nav>
      <a href="../index.html">首页</a>
      <a href="#categories">分类榜</a>
      <a href="../deep-dive.html" class="active">深度拆解</a>
      <a href="../about.html">关于</a>
    </nav>
  </div>
</header>

<main class="wrap page-main deep-page">
  <div class="page-head">
    <h1>{esc(d["name"])}</h1>
    <div class="deep-meta">
      <a href="{esc(d["url"])}" target="_blank" rel="noopener" class="repo-link">{esc(d["url"])}</a>
      <span class="stars">★ {fmt(d.get("stars",0))}</span>
      {f'<span class="lang">{esc(d.get("language",""))}</span>' if d.get("language") else ''}
      {f'<span class="growth growth-hot">+{fmt(d.get("growth_30d"))} /30d</span>' if d.get("growth_30d") is not None else ''}
    </div>
  </div>

  <p class="deep-lead">{esc(d.get("summary",""))}</p>
  <div class="deep-topics">{tags}</div>
  {metrics}

  <div class="deep-sections">
{sections_joined}
  </div>

  <div class="deep-verdict">
    <h4>我的结论</h4>
    <p>{esc(d.get("verdict",""))}</p>
  </div>

  <nav class="deep-nav">
    {prev_html}
    <a href="../deep-dive.html" class="nav-link index">返回目录</a>
    {next_html}
  </nav>
</main>

<footer class="site-footer">
  <div class="wrap"><p class="muted">用 GitHub 公开 API 数据整理 · 独立页面：deep-dive/{deep_slug(d['name'])}.html</p></div>
</footer>
</body>
</html>"""


def render_deep_index(all_deep, short_notes, projects):
    """deep-dive.html 索引页：全部短评 + 12 篇深度卡片。"""
    # 把 short_notes 按 projects.json 的分类归类
    cats = projects.get("categories", {})
    cat_items = {}
    for cid, _, _ in CATEGORIES:
        cat_items[cid] = []
    for p in sum((cats.get(cid, []) for cid, _, _ in CATEGORIES), []):
        fn = p.get("full_name")
        if fn and fn in short_notes:
            cat_items.setdefault(p.get("category", ""), []).append((fn, short_notes[fn], p))

    note_blocks = []
    for cid, cname, cdesc in CATEGORIES:
        items = cat_items.get(cid, [])
        if not items:
            continue
        notes = "\n".join(render_short_note(fn, n) for fn, n, _ in items)
        note_blocks.append(f"""    <section class="cat-section" id="cat-{cid}">
      <div class="section-head">
        <h2>{esc(cname)}</h2>
        <p>{esc(cdesc)}</p>
      </div>
      <div class="notes-grid">
{notes}
      </div>
    </section>""")
    note_blocks_joined = "\n".join(note_blocks)
    deep_cards_joined = "\n".join(render_deep_card(d) for d in all_deep)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>深度拆解 · GitHub 冲浪手记</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html"><span class="brand-mark">🌊</span><span>GitHub 冲浪手记</span></a>
    <nav>
      <a href="index.html">首页</a>
      <a href="#categories">分类榜</a>
      <a href="deep-dive.html" class="active">深度拆解</a>
      <a href="about.html">关于</a>
    </nav>
  </div>
</header>

<main class="wrap page-main">
  <div class="page-head">
    <h1>深度拆解</h1>
    <p class="lede">
      下面是全部收录项目的简短手记，以及 12 篇我重点拆解的深度文章。短评帮你快速筛选，
      深度文章里我翻开了 README、看过目录结构，写下可落地的判断。
    </p>
  </div>

  <section class="wrap">
    <div class="section-head">
      <h2>🧠 重点深度拆解（12 篇）</h2>
      <p>每篇都读过 README 与源码结构，包含架构判断、安装门槛与我的结论。</p>
    </div>
    <div class="deeps-grid">
{deep_cards_joined}
    </div>
  </section>

  <section class="wrap" id="categories">
    <div class="section-head">
      <h2>📋 全部项目简短手记</h2>
      <p>共 {len(short_notes)} 条，每条一句定语 + 适合人群 + 一个钩子，供你快速决定是否点进去。</p>
    </div>
{note_blocks_joined}
  </section>
</main>

<footer class="site-footer">
  <div class="wrap"><p class="muted">用 GitHub 公开 API 数据整理</p></div>
</footer>
</body>
</html>"""


def render_growth(all_deep, projects):
    """growth.html 成长档案页。"""
    latest = projects.get("generated_at", "")[:10]
    total = sum(len(projects.get("categories", {}).get(cid, [])) for cid, _, _ in CATEGORIES)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>成长档案 · GitHub 冲浪手记</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html"><span class="brand-mark">🌊</span><span>GitHub 冲浪手记</span></a>
    <nav>
      <a href="index.html">首页</a>
      <a href="#categories">分类榜</a>
      <a href="deep-dive.html">深度拆解</a>
      <a href="growth.html" class="active">成长档案</a>
    </nav>
  </div>
</header>

<main class="wrap page-main">
  <div class="page-head">
    <h1>成长档案</h1>
    <p class="lede">记录自己在开源里的实践与迁移：从「看热闹」到「读源码」、从「抄链接」到「写拆解」。</p>
  </div>

  <section class="wrap">
    <div class="section-head">
      <h2>📊 本期数据快照</h2>
    </div>
    <div class="growth-stats">
      <div class="stat"><strong>{total}</strong><span>收录项目</span></div>
      <div class="stat"><strong>{len(CATEGORIES)}</strong><span>分类榜单</span></div>
      <div class="stat"><strong>{len(all_deep)}</strong><span>深度拆解文章</span></div>
      <div class="stat"><strong>{latest}</strong><span>最近更新</span></div>
    </div>
  </section>

  <section class="wrap">
    <div class="section-head">
      <h2>🛠️ 我正在做的迁移</h2>
    </div>
    <ul class="growth-list">
      <li><strong>多 agent 专化 vs 并行化：</strong>把每个未完成项目拆成子任务 DAG，按并发容量决定哪些交给通用 agent 并行，哪些单点特化。</li>
      <li><strong>superpowers-core v1.0：</strong>构建 wheel 已落盘，等待 PyPI/GitHub 发布凭据后上线。</li>
      <li><strong>M3U8 广告屏蔽插件：</strong>核心检测引擎 9/9 测试通过，Manifest V3 插件已构建打包，等待商店发布凭据。</li>
      <li><strong>DEEPDIVE 站点：</strong>12 篇 A 标准深度拆解已重写，独立页面与索引页正在生成。</li>
    </ul>
  </section>

  <section class="wrap">
    <div class="section-head">
      <h2>🧭 下一步</h2>
    </div>
    <ul class="growth-list">
      <li>为 12 篇深度拆解补足 ≥800 字 A 标准正文（README + 源码结构双验证）。</li>
      <li>本地渲染全部页面并校验链接。</li>
      <td>通过 push.sh 推送到 GitHub Pages main 分支上线。</td>
    </ul>
  </section>
</main>

<footer class="site-footer">
  <div class="wrap"><p class="muted">用 GitHub 公开 API 数据整理 · 成长档案持续更新中</p></div>
</footer>
</body>
</html>"""


def render_home(data, short_notes, weekly_changes=None):
    latest = data.get("generated_at", "")[:10]
    total = sum(len(data["categories"].get(c, [])) for c, _, _ in CATEGORIES)
    hero_picks = data.get("hero_picks", [])

    hero_cards = "\n".join(render_card(p, featured=True) for p in hero_picks)

    cat_cards = []
    for cid, cname, cdesc in CATEGORIES:
        items = data["categories"].get(cid, [])
        top = items[0] if items else None
        cat_cards.append(f"""      <a class="cat-card" href="#cat-{cid}">
        <h3>{esc(cname)}</h3>
        <p>{esc(cdesc)}</p>
        <span class="cat-count">{len(items)} 个项目</span>
        {f'<span class="cat-lead">领跑：{esc(top["full_name"])}</span>' if top else ''}
      </a>""")

    weekly_changes_html = render_weekly_changes(weekly_changes)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>zcoriander.github.io · GitHub 冲浪手记</title>
<meta name="description" content="一个开源新人的 GitHub 冲浪手记：收集热门、有趣、有用的开源项目，记录踩坑与思考。">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html">
      <span class="brand-mark">🌊</span>
      <span>GitHub 冲浪手记</span>
    </a>
    <nav>
      <a href="index.html" class="active">首页</a>
      <a href="#categories">分类榜</a>
      <a href="deep-dive.html">深度拆解</a>
      <a href="about.html">关于</a>
      <a href="growth.html">成长档案</a>
    </nav>
  </div>
</header>

<main>
  <section class="hero wrap">
    <p class="eyebrow">开源新人的每周冲浪</p>
    <h1>在 GitHub 的海洋里，<br>捞点真正有用的东西。</h1>
    <p class="lede">
      我是个开源新人。但新人也有新人的看法——
      每周翻遍仓库列表，挑出<strong>热门、有趣、真能上手</strong>的项目，
      顺便记下我的想法和踩过的坑。
    </p>
    <div class="hero-stats">
      <div class="stat"><strong>{total}</strong><span>本次收录项目</span></div>
      <div class="stat"><strong>{len(CATEGORIES)}</strong><span>分类榜单</span></div>
      <div class="stat"><strong>{latest}</strong><span>最近更新</span></div>
    </div>
  </section>

  <section class="wrap" id="hero-picks">
    <div class="section-head">
      <h2>✨ 本期我最想安利</h2>
      <p>不是最热的那几个，是我觉得<strong>你今天就应该点进去看看</strong>的那几个</p>
    </div>
    <div class="cards">
{hero_cards}
    </div>
  </section>

  {weekly_changes_html}

  <section class="wrap" id="categories">
    <div class="section-head">
      <h2>📂 分类榜单</h2>
      <p>每个分类固定 10 个，可以横向对比，也可以当索引用</p>
    </div>
    <div class="cat-grid">
{chr(10).join(cat_cards)}
    </div>
  </section>

  <section class="wrap">
    <div class="section-head">
      <h2>🧭 我的冲浪方法</h2>
    </div>
    <div class="method">
      <div class="method-item">
        <span class="method-num">01</span>
        <h4>不只看 Star</h4>
        <p>Star 是热度不是质量。我同时看最近提交时间、Issue 响应、许可证和文档完整度。</p>
      </div>
      <div class="method-item">
        <span class="method-num">02</span>
        <h4>常青榜看增速</h4>
        <p>老牌巨头的 star 总量几乎不动，榜单会永远那几个。所以常青榜改用近 30 天增长排序，看谁在悄悄上位。</p>
      </div>
      <div class="method-item">
        <span class="method-num">03</span>
        <h4>亲自读 README</h4>
        <p>每个分类我会挑几个真正翻开 README、跑过安装命令的项目，细节都在深度拆解里。</p>
      </div>
      <div class="method-item">
        <span class="method-num">04</span>
        <h4>记录想法</h4>
        <p>看到有意思的架构、坑、趋势，我会写进手记。不只是搬运，是消化后的判断。</p>
      </div>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="wrap">
    <p>用 GitHub 公开 API 数据整理 · 最后更新 {latest}</p>
    <p class="muted">开源内容版权归各自作者所有。此站仅为学习笔记与索引。</p>
  </div>
</footer>
</body>
</html>"""


def render_weekly_changes(weekly_changes):
    """首页本周榜单变动板块：新加入、被顶替、排名变动。"""
    if not weekly_changes or weekly_changes.get("note"):
        return f"""    <section class="wrap" id="weekly-changes">
      <div class="section-head">
        <h2>📈 本周榜单变动</h2>
        <p class="muted">暂无变动数据（首次运行或等待下周一更新）</p>
      </div>
    </section>"""

    new_entries = weekly_changes.get("new_entries", [])
    out_entries = weekly_changes.get("out_entries", [])
    moved_entries = weekly_changes.get("moved_entries", [])
    week_start = weekly_changes.get("week_start", "")

    def change_card(p, is_out=False):
        cat_html = f'<span class="cat">{esc(p.get("category",""))}</span>' if not is_out else f'<span class="cat prev-cat">原 {esc(p.get("prev_category",""))}</span>'
        return f"""          <article class="change-card">
            <a class="repo" href="https://github.com/{esc(p['full_name'])}" target="_blank" rel="noopener">
              {esc(p['full_name'])}
            </a>
            {cat_html}
            <span class="stars">★ {fmt(p.get("stars",0))}</span>
          </article>"""

    new_html = "\n".join(change_card(p) for p in new_entries) or '<p class="muted">本周无新加入</p>'
    out_html = "\n".join(change_card(p, is_out=True) for p in out_entries) or '<p class="muted">本周无项目被顶替</p>'
    moved_html = "\n".join(change_card(p) for p in moved_entries) or '<p class="muted">本周无排名变动</p>'

    return f"""    <section class="wrap" id="weekly-changes">
      <div class="section-head">
        <h2>📈 本周榜单变动</h2>
        <p>每周一更新 · 数据周期：{week_start}</p>
      </div>
      <div class="changes-grid">
        <div class="change-block change-new">
          <h3>🆕 新加入（共{len(new_entries)}个）</h3>
          <div class="change-cards">
{new_html}
          </div>
        </div>
        <div class="change-block change-out">
          <h3>📉 被顶替（共{len(out_entries)}个）</h3>
          <div class="change-cards">
{out_html}
          </div>
        </div>
        <div class="change-block change-moved">
          <h3>📊 排名变动（共{len(moved_entries)}个）</h3>
          <div class="change-cards">
{moved_html}
          </div>
        </div>
      </div>
    </section>"""


def render_categories(data):
    blocks = []
    for cid, cname, cdesc in CATEGORIES:
        items = data.get("categories", {}).get(cid, [])
        if not items:
            continue
        cards = "\n".join(render_card(p) for p in items)
        note = data.get("category_notes", {}).get(cid, "")
        note_html = f'<p class="cat-note">{esc(note)}</p>' if note else ""
        blocks.append(f"""    <section class="cat-section" id="cat-{cid}">
      <div class="section-head">
        <h2>{esc(cname)}</h2>
        <p>{esc(cdesc)}</p>
        {note_html}
      </div>
      <div class="cards">
{cards}
      </div>
    </section>""")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>分类榜单 · GitHub 冲浪手记</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html"><span class="brand-mark">🌊</span><span>GitHub 冲浪手记</span></a>
    <nav>
      <a href="index.html">首页</a>
      <a href="#categories" class="active">分类榜</a>
      <a href="deep-dive.html">深度拆解</a>
      <a href="about.html">关于</a>
      <a href="growth.html">成长档案</a>
    </nav>
  </div>
</header>

<main class="wrap page-main">
  <div class="page-head">
    <h1>分类榜单</h1>
    <p class="lede">每个分类 10 个项目。相同分类内部按推荐分排序，不是单纯按 star 数。</p>
  </div>
  <nav class="jump">
    {''.join(f'<a href="#cat-{cid}">{esc(cname)}</a>' for cid, cname, _ in CATEGORIES)}
  </nav>
{chr(10).join(blocks)}
</main>

<footer class="site-footer">
  <div class="wrap">
    <p class="muted">用 GitHub 公开 API 数据整理</p>
  </div>
</footer>
</body>
</html>"""


def render_about(data):
    thoughts = data.get("thoughts", [])
    thought_html = "".join(f"""    <div class="thought">
      <div class="thought-date">{esc(t.get("date",""))}</div>
      <h3>{esc(t.get("title",""))}</h3>
      <p>{esc(t.get("body",""))}</p>
      {f'<p class="thought-links">' + ''.join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(n)}</a>' for n,u in t.get("links",[])) + '</p>' if t.get("links") else ''}
    </div>""" for t in thoughts)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>关于 · GitHub 冲浪手记</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html"><span class="brand-mark">🌊</span><span>GitHub 冲浪手记</span></a>
    <nav>
      <a href="index.html">首页</a>
      <a href="#categories">分类榜</a>
      <a href="deep-dive.html">深度拆解</a>
      <a href="about.html" class="active">关于</a>
      <a href="growth.html">成长档案</a>
    </nav>
  </div>
</header>

<main class="wrap page-main">
  <div class="page-head">
    <h1>关于这个站</h1>
    <p class="lede">一个开源新人的私人冲浪笔记本。</p>
  </div>

  <section class="prose">
    <h2>我是谁</h2>
    <p>一个刚进 GitHub 门的新人程序员。踩过的坑不少，但每次挖到好项目都特别兴奋，就想记下来分享。</p>
    <p>这个站是我的两件事合起来：<strong>每周的 GitHub 冲浪榜单</strong>，和<strong>随手记下的想法</strong>。</p>

    <h2>榜单是怎么来的</h2>
    <p>全部数据来自 GitHub 公开 API（搜索 + 仓库详情接口），每次更新都会重新抓一遍。分类和排序规则写在首页的"冲浪方法"里，欢迎来挑刺。</p>

    <h2>关于「常青经典」这一栏</h2>
    <p>很多榜单按 star 总数排，结果永远是那几个老面孔——因为它们的 star 早就不怎么涨了，总数自然不动。</p>
    <p>所以这一栏我换了个思路：<strong>用近 30 天的 star 增量排序</strong>。同样的老牌项目，有的还在稳步增长，有的其实早就停滞了。排出来的结果会告诉你谁在悄悄上位。</p>

    <h2>安全说明</h2>
    <p>本站的自动化脚本通过环境变量或本地受限文件读取 GitHub token，<strong>token 不会写入任何仓库、不会进入页面内容</strong>。详细方案见仓库里的 <code>docs/SECURITY.md</code>。</p>
  </section>

  <section class="prose">
    <h2>📝 手记与想法</h2>
    <p>这里放我在冲浪过程中的观察、困惑和一些还没想明白的事。</p>
    {thought_html}
  </section>
</main>

<footer class="site-footer">
  <div class="wrap"><p class="muted">用 GitHub 公开 API 数据整理</p></div>
</footer>
</body>
</html>"""


def main():
    projects = load_json(PROJECTS, {"categories": {}, "generated_at": "", "hero_picks": [], "thoughts": [], "category_notes": {}})
    short_notes = load_json(SHORT_NOTES, {})
    all_deep = load_json(DEEP_DIVES, {"deep_dives": []}).get("deep_dives", [])
    weekly_changes = load_json(os.path.join(DATA, "weekly_changes.json"), None)
    # 按 DEEP_ORDER 排序，缺失的补空
    by_name = {d["name"]: d for d in all_deep}
    ordered_deep = [by_name[n] for n in DEEP_ORDER if n in by_name]

    os.makedirs(DEEP_OUT, exist_ok=True)

    outputs = {
        "index.html": render_home(projects, short_notes, weekly_changes),
        "categories.html": render_categories(projects),
        "deep-dive.html": render_deep_index(ordered_deep, short_notes, projects),
        "about.html": render_about(projects),
        "growth.html": render_growth(ordered_deep, projects),
    }
    for name, content in outputs.items():
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ {name} ({len(content):,} bytes)")

    # 每篇深度拆解独立页面
    for d in ordered_deep:
        content = render_deep_detail(d, ordered_deep)
        path = os.path.join(DEEP_OUT, f"{deep_slug(d['name'])}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ deep-dive/{deep_slug(d['name'])}.html ({len(content):,} bytes)")

    print("站点生成完成")


if __name__ == "__main__":
    main()
