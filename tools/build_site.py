#!/usr/bin/env python3
"""
build_site.py — 从 data/projects.json 生成 GitHub Pages 静态站点。

设计原则：
- 纯静态、零构建依赖、无需 Node
- 每个分类固定 10 条，用户可横向对比
- 「最高 Star」类特殊处理：star 总量几乎不变，改用「近 30 天 star 增长」
  作为排序信号，避免榜单年年雷同
"""
import json, os, html, datetime, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "projects.json")
OUT = ROOT

CATEGORIES = [
    ("hot_week",   "🔥 本周最热",   "新鲜上架，增速最快的一批"),
    ("new_star",   "🌱 黑马新星",   "三个月内冒头，冲劲十足"),
    ("beginner",   "🛠️ 新手友好",   "文档齐全、门槛低，第一份贡献从这里开始"),
    ("fun",        "💡 奇思妙想",   "脑洞和好玩，逛着逛着就学会了"),
    ("learning",   "📚 学习资源",   "系统学习路径，照着走不迷路"),
    ("evergreen",  "🏛️ 常青经典",   "星标王座变动不大，我们用增速来看新秩序"),
]


def esc(s):
    return html.escape(s or "", quote=True)


def fmt(n):
    if n >= 1000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    return str(n)


def parse_repo(full_name):
    return full_name.split("/")[-1]


def render_card(p, featured=False):
    """单张项目卡片"""
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


def render_home(data):
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


def render_categories(data):
    blocks = []
    for cid, cname, cdesc in CATEGORIES:
        items = data["categories"].get(cid, [])
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


def render_deep_dive(data):
    items = data.get("deep_dives", [])
    blocks = []
    for d in items:
        tags = "".join(f'<span class="topic">{esc(t)}</span>' for t in d.get("tags", []))
        sections = []
        for s in d.get("sections", []):
            body = "\n".join(f"<p>{esc(p)}</p>" for p in s.get("paragraphs", []))
            bullets = ""
            if s.get("bullets"):
                bullets = "<ul>" + "".join(f"<li>{esc(b)}</li>" for b in s["bullets"]) + "</ul>"
            sections.append(f"""        <h3>{esc(s["title"])}</h3>
        {body}
        {bullets}""")
        metrics = ""
        if d.get("metrics"):
            metrics = '<div class="metrics">' + "".join(
                f'<div class="metric"><strong>{esc(m[0])}</strong><span>{esc(m[1])}</span></div>'
                for m in d["metrics"]
            ) + "</div>"
        blocks.append(f"""    <article class="deep">
      <div class="deep-head">
        <h2><a href="{esc(d["url"])}" target="_blank" rel="noopener">{esc(d["name"])}</a></h2>
        <div class="deep-meta">
          <span class="stars">★ {fmt(d.get("stars",0))}</span>
          {f'<span class="lang">{esc(d["language"])}</span>' if d.get("language") else ''}
          {f'<span class="growth growth-hot">+{fmt(d["growth_30d"])} /30d</span>' if d.get("growth_30d") is not None else ''}
        </div>
      </div>
      <p class="deep-sub">{esc(d.get("summary",""))}</p>
      <div class="topics">{tags}</div>
      {metrics}
{chr(10).join(sections)}
      <div class="deep-verdict">
        <h4>我的结论</h4>
        <p>{esc(d.get("verdict",""))}</p>
      </div>
    </article>""")

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
    <p class="lede">不只是贴链接。我真的翻开了 README、看了目录结构、想了想它为什么火。</p>
  </div>
{chr(10).join(blocks)}
</main>

<footer class="site-footer">
  <div class="wrap"><p class="muted">用 GitHub 公开 API 数据整理</p></div>
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
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    outputs = {
        "index.html": render_home(data),
        "categories.html": render_categories(data),
        "deep-dive.html": render_deep_dive(data),
        "about.html": render_about(data),
    }
    for name, content in outputs.items():
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ {name} ({len(content):,} bytes)")

    print("站点生成完成")


if __name__ == "__main__":
    main()
