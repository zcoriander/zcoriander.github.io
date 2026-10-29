#!/usr/bin/env python3
"""
enrich.py — 为 projects.json 补充深度拆解文案与手记想法。

文案分两层：
  1. 自动生成的「事实层」：指标、标签、最近提交等，从 API 数据填充
  2. 人工撰写的「判断层」：我对每个项目的看法、结论

这样做的目的是：事实永远来自真实 API 数据，判断和事实分离，
将来更新时只要重跑 collect.py 就能保留判断、刷新事实。
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "projects.json")


def fmt(n):
    if n is None:
        return "—"
    if n >= 1000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    return str(n)


# 人工撰写的深度分析：key = full_name
# 每个项目包含 summary / sections / verdict
DEEP_CONTENT = {
    "openclaw/openclaw": {
        "summary": "把 AI 助手部署在你自己的机器上，然后让它住进你已经在用的聊天软件里。Discord、iMessage、Slack、WhatsApp、Telegram……20 多个平台，一个 Gateway 统一调度。",
        "sections": [
            {
                "title": "它到底在做什么",
                "paragraphs": [
                    "一句话：本地跑的 AI 助手 + 一个叫 Gateway 的控制平面。Gateway 负责会话、工具调用、事件和渠道连接，助手本体通过插件机制对接 Claude、Codex 或本地模型。",
                    "关键点是它不打算取代你的聊天软件，而是「住进去」。个人版跑在笔记本上，团队版跑在服务器上——作者说区别只是配置文件。"
                ],
                "bullets": [
                    "状态、记忆、凭证全部留在自己硬件上",
                    "模型是可替换插件，换模型不用动其他配置",
                    "由 OpenClaw Foundation（501(c)(3) 独立基金会）托管，没有付费层"
                ],
            },
            {
                "title": "让我在意的架构选择",
                "paragraphs": [
                    "README 里有一句话我反复看了两遍：trusted gateway, untrusted execution, policy enforced by code——可信网关、不可信执行、策略由代码强制。",
                    "这和很多「把 Agent 塞进沙箱里跑」的方案是反的。它的思路是：执行环境（工具、命令、文件）是不可信边界内的，所以权限判定必须在网关这一层用代码写死，而不是指望被调用的那部分自觉。",
                    "另外它默认只做每日版本检查，匿名功能统计是 opt-in，遥测可以完全关掉。对一个要常驻在你所有聊天窗口里的东西来说，这个默认值设置是加分项。"
                ],
            },
            {
                "title": "安装门槛",
                "paragraphs": [
                    "一条 curl 命令或一条 npm 命令，跨 macOS / Linux / Windows。装完自动跑引导流程，验证模型连通性、创建工作区、配置 Gateway。",
                    "Node.js 版本要求比较新（24.22.1+ 或 26.12.1+），这算是个小门槛——但换来的是不用自己拼装依赖。"
                ],
            },
        ],
        "verdict": "如果你想要一个「常驻在聊天软件里的私人助手」，目前生态里最完整的开源方案之一。架构上「策略由代码强制」那句话值得所有做 Agent 的人抄在墙上。适合有一定技术基础、愿意自己管一台机器的人；完全零基础的话，20 多个渠道的配置量会有点劝退。",
    },
    "obra/superpowers": {
        "summary": "一套给编码 Agent 用的完整开发方法论——不是几个提示词，而是一套带自动触发机制的工作流。",
        "sections": [
            {
                "title": "核心思路：先谈清楚，再写代码",
                "paragraphs": [
                    "它在你启动编码 Agent 的那一刻就介入。Agent 不会直接开始写代码，而是先退一步问你到底想做什么。",
                    "从对话里提炼出规格之后，它会分成你「读得完、咽得下」的小块给你看。你签字确认设计，然后它给出实现计划——README 里形容这个计划要清晰到「一个热情但品味糟糕、没判断力、不了解项目背景、还讨厌写测试的初级工程师」都能照着做。",
                    "这描述挺刻薄的，但很诚实：它假设执行者不会替你思考，所以计划必须自带上下文。"
                ],
            },
            {
                "title": "执行阶段：子 Agent 流水线",
                "paragraphs": [
                    "你说「go」之后，它启动一个子 Agent 驱动的开发流程：Agent 逐个任务往下推进，自己检查和审查自己的工作，然后继续。",
                    "README 里说它「连续自主工作几小时不偏离计划」并不罕见。同时强制真·红绿 TDD、YAGNI 和 DRY。"
                ],
                "bullets": [
                    "规格先行的设计评审，避免一上来就写",
                    "子 Agent 承担实现与自审",
                    "方法论约束（TDD / YAGNI / DRY）内建在技能里"
                ],
            },
            {
                "title": "生态兼容性",
                "paragraphs": [
                    "这是我觉得它最聪明的地方：支持面极广——Claude Code、Codex、Cursor、Copilot CLI、Gemini CLI、OpenCode、Qwen Code、Hermes Agent……十几种 harness 都能装。",
                    "因为它把方法论做成了「可组合的技能 + 少量初始指令」，而不是绑死在某一个产品上。这让它更像是「Agent 时代的 GDD 文档」。"
                ],
            },
        ],
        "verdict": "如果你团队在用 AI 编码工具但产出质量忽高忽低，缺的不是模型而是流程约束。这个项目提供的正是流程。而且它明确反对「 vibe coding 」，跟我的看法一致：AI 降低了写代码的门槛，但没降低想清楚要什么的门槛。",
    },
    "mattpocock/skills": {
        "summary": "作者每天在用的 Agent 技能包，定位很明确：给「做真实工程」用，不是给 vibe coding 用。",
        "sections": [
            {
                "title": "它反对什么",
                "paragraphs": [
                    "README 里点名了 GSD、BMAD、Spec-Kit 这类方案：它们试图通过「接管整个流程」来帮助开发者，代价是你失去了控制权，而且流程里出的 bug 很难排查。",
                    "作者的选择是完全相反的：技能要小、易改、可组合，跟模型无关。"
                ],
                "bullets": [
                    "刻意做得小而可组合",
                    "不绑定特定模型",
                    "设计上允许你「随便改，改成自己的」"
                ],
            },
            {
                "title": "安装方式体现了设计哲学",
                "paragraphs": [
                    "推荐用 skills.sh 把可编辑的文件直接拷进你的项目，然后你自己维护更新——注意它建议你「每个 agent 选一个」，装两个会导致每个技能出现两遍。",
                    "这种「拷贝文件而不是装插件」的方式，代价是要手动更新，收益是你能完全掌控内容、也能按自己的团队习惯改写。"
                ],
            },
            {
                "title": "为什么这类项目现在重要",
                "paragraphs": [
                    "把「资深工程师的隐性经验」变成 Agent 可执行的技能文件，本质上是在做知识的显性化。",
                    "这也解释了为什么 2026 年会有大量同类仓库涌出——当 Agent 能力趋同，真正的差异化就落到了「你给它喂什么方法论」上。"
                ],
            },
        ],
        "verdict": "和 Superpowers 是一对镜像：superpowers 是重流程、可自动触发；这个是轻流程、完全可控。两者都指向同一件事——AI 编码的瓶颈已经从「模型能不能写」转移到「流程约束得好不好」。想快速起步用前者，想深度定制用后者。",
    },
    "shareAI-lab/learn-claude-code": {
        "summary": "从零手写一个 Claude Code 风格的 Agent Harness，重点不是用 Claude Code，而是理解它为什么这么设计。",
        "sections": [
            {
                "title": "核心论点",
                "paragraphs": [
                    "README 开头那句话很清醒：Agency comes from the model. An agent product = model + harness. 智能来自模型训练，不是外部代码编排。模型是驾驶员，harness 是车。这个仓库教你怎么造那辆车。",
                    "接着它用三个历史案例论证——DeepMind DQN 打 Atari（2013）、OpenAI Five 打 Dota 2（2019）、AlphaStar 打星际争霸 2（2019）——说明能动性是学出来的，不是编排出来的。"
                ],
            },
            {
                "title": "它和 Superpowers 的关系",
                "paragraphs": [
                    "两个项目放在一起看很有意思：learn-claude-code 是「造车厂」，superpowers 是「驾驶规范」。",
                    "前者让你理解 harness 的每个零件为什么存在，后者规定拿到车之后该怎么开。"
                ],
                "bullets": [
                    "用 Bash 从零实现一个 nano 级的 agent harness",
                    "配套中文/日文翻译，学习门槛低",
                    "有 Trendshift 徽章，说明在新生代项目里热度很高"
                ],
            },
        ],
        "verdict": "这是我在这批项目里最推荐给「想理解而不是想直接用」的人的项目。README 的写作质量在开源项目里属于头部——论述清晰、有历史纵深、有明确的观点。读完你会发现，很多「AI 编程工具」的差异，本质是 harness 设计哲学的差异。",
    },
    "ssloy/tinyrenderer": {
        "summary": "500 行裸 C++ 实现软件渲染器，用来教人搞明白 OpenGL / Vulkan / Metal / DirectX 底下到底发生了什么。",
        "sections": [
            {
                "title": "为什么它还是值得看",
                "paragraphs": [
                    "作者自己说「代码本身没什么意思」，重点在配套的 14 篇课程笔记。这句话本身就是一种克制——它不假装是个库，就是一套教案。",
                    "课程从 Bresenham 直线算法开始，经过三角形光栅化、重心坐标、隐藏面剔除、z-buffer、相机处理、着色、纹理、法线映射、阴影映射、SSAO，最后来个 toon shading 收尾。"
                ],
                "bullets": [
                    "零第三方库，包括图形库",
                    "作者说自己的学生学完后能写出相当不错的渲染器",
                    "配套站点 haqr.eu 有完整中文/多语言笔记"
                ],
            },
            {
                "title": "它教会你的思维方式",
                "paragraphs": [
                    "这其实是一套「逆向学习法」：先手写出最简实现，再回头理解每个图形 API 背后在做什么。",
                    "作为新人，我觉得这种学习路径特别值得借鉴——先用最笨的办法跑通，再补理论。比反过来先啃一千页图形学教材有效得多。"
                ],
            },
        ],
        "verdict": "24k star 里我最推荐的一个。它代表了一类被低估的项目：代码量小得离谱，但它教的东西能迁移到你写的每一行图形/系统代码里。适合当作「学底层」的自修教材。",
    },
    "codecrafters-io/build-your-own-x": {
        "summary": "从零复刻你喜欢的技术：数据库、操作系统、编译器、容器、Docker、Git……全是教程。",
        "sections": [
            {
                "title": "这个仓库的特殊之处",
                "paragraphs": [
                    "557k star，全球 star 数最高的仓库之一。但它本质上不是代码库，而是一张巨大的索引表——每一行指向一个「自己实现一遍 X」的教程。",
                    "涵盖范围从数据库（SQLite、Redis、PostgreSQL）、操作系统（Linux、Unix shell、终端）、编译器（Bash、LLVM、Go）、容器（Docker、Kubernetes）、网络（TCP、HTTP）、到浏览器（Chrome）、游戏引擎、神经网络、GUI 框架，甚至「自己写一个 Git」和「自己写一个 Neural Network」。"
                ],
                "bullets": [
                    "Build your own X 系列是经典，很多教程配套完整的课程站点",
                    "覆盖从入门到编译器级别，难度梯度清晰",
                    "每个条目通常都标注了难度和前置知识"
                ],
            },
            {
                "title": "为什么这类项目长青",
                "paragraphs": [
                    "它的价值不随技术栈变化。框架会换，但「理解数据库索引是怎么工作的」这件事不会过时。",
                    "对比一下：它的 star 增长很慢（老项目常态），但社区活跃度一直不低，因为总有人在学新东西，也在持续贡献新的「X」。"
                ],
            },
        ],
        "verdict": "如果只能推荐一个「学习索引」，就是它。star 数 557k 说明它被反复验证过——但更重要的是它把「我想搞懂 X」变成了一条明确的行动路径。",
    },
    "donnemartin/system-design-primer": {
        "summary": "大规模系统设计的学习指南，还附带了 Anki 记忆卡，直接对着面试准备。",
        "sections": [
            {
                "title": "它解决什么问题",
                "paragraphs": [
                    "系统设计面试是新手最焦虑的环节之一：题目开放，不知道从哪答起。这个仓库把答题的骨架给拆好了。",
                    "内容从「如何回答一个系统设计问题」开始，然后逐个讲：缓存、数据库、负载均衡、缓存穿透/雪崩/击穿、限流、消息队列、一致性哈希、复制、分片、CAP 定理……还配了插图。"
                ],
                "bullets": [
                    "每节都配 Anki 记忆卡，能直接导入做间隔重复",
                    "包含真实系统案例（Twitter、Netflix 等）",
                    "有中英等多语言翻译版本"
                ],
            },
        ],
        "verdict": "它的 Anki 卡片设计是我最喜欢的一点——把「读过」变成「记得住」。这比单纯又一个 Markdown 教程务实得多。新人如果正准备系统设计面试，这是最高性价比的起点。",
    },
    "freeCodeCamp/freeCodeCamp": {
        "summary": "全球最大的免费编程学习平台，458k star，课程本身也是开源的。",
        "sections": [
            {
                "title": "不一样的定位",
                "paragraphs": [
                    "它是「免费学编程」这件事的答案：不是一门课，是一整条课程体系——HTML/CSS/JS 到数据可视化、证书项目，每一节都能在浏览器里直接写代码并即时看到结果。",
                    "更特别的是它的商业模式：完全免费，运营靠捐款。这让它没有必须「尽快让你升级付费」的焦虑，课程节奏是真的按学习者来设计的。"
                ],
                "bullets": [
                    "TypeScript 技术栈，代码完全开源",
                    "浏览器内直接运行，无需本地环境",
                    "社区规模巨大，互助氛围浓"
                ],
            },
            {
                "title": "为什么它值得注意",
                "paragraphs": [
                    "作为一个「学习资源」类项目，它常年保持高活跃度提交——这在老牌教程仓库里不常见。说明它还在积极维护，不是在吃老本。"
                ],
            },
        ],
        "verdict": "如果你完全零基础，它是最稳的起点。缺点是它教的是 web 开发，如果你的目标是后端、系统或 AI，直接看它的证书项目有点绕——但那个项目本身质量不错，可以当跳板。",
    },
    "firstcontributions/first-contributions": {
        "summary": "专门用来教新手完成第一次开源贡献的仓库，56k star。",
        "sections": [
            {
                "title": "设计得极巧",
                "paragraphs": [
                    "它的思路很聪明：让你去改一个你自己的练习仓库（练习分支），而不是直接改真实的热门项目。",
                    "流程是：fork → clone → 建分支 → 改一处 → commit → push → 开 PR。目标是让你在真正动手前完整走一遍整个协作流程，把陌生感消掉。"
                ],
                "bullets": [
                    "步骤图文清晰，几乎没有理解门槛",
                    "专门为「第一次」设计，而不是「又一次」",
                    "有中文等多语言版本"
                ],
            },
            {
                "title": "为什么这一步很重要",
                "paragraphs": [
                    "很多人卡在第一次贡献不是技术问题，是心理门槛：不知道流程、不敢提 PR、怕被拒。",
                    "这个仓库把流程拆解到每一步都给出确切命令，把第一次的心理成本降到最低。做完一遍之后，再面对真实项目就顺了。"
                ],
            },
        ],
        "verdict": "如果你的目标是「今年开始给开源做贡献」，这是最该先跑一遍的东西。半小时的投入，回报是拆掉一整层心理障碍。",
    },
}


# 人工撰写的手记
THOUGHTS = [
    {
        "date": "2026-10-29",
        "title": "star 数是个越来越不可靠的信号",
        "body": "今天做这个站的时候踩到一个坑：我本来想按「近 30 天 star 增长」给常青榜排序，结果发现 GitHub 的 stargazers 时间戳接口必须认证才能用，未认证直接 401。这件事本身挺有意思——GitHub 刻意把「谁什么时候 star 了」当成需要登录才能看的数据，大概是防刷号和隐私考虑。但这意味着一个结果：star 总数是公开的，star 的变化过程是半公开的。所以很多榜单只能按总数排，于是老牌项目永远霸榜，哪怕它们早就不动了。我现在的解法是未认证时退化用「近 90 天提交数」当活跃度信号，配了 token 就能用真正的 star 增速。",
        "links": [
            ("GitHub REST API 文档", "https://docs.github.com/en/rest/activity/starring#list-stargazers"),
        ],
    },
    {
        "date": "2026-10-29",
        "title": "2026 年的新项目开始「自带方法论」了",
        "body": "今天翻项目的时候发现一个明显的趋势：superpowers、mattpocock/skills、affaan-m/ECC 这类新起的老大不高但 star 涨得快的仓库，主打的都不是「更强的模型」或「更快的推理」，而是「怎么让 AI 写代码更靠谱」。它们把资深工程师的隐性经验——先设计再动手、小步提交、红绿重构、不要 vibe coding——写成 Agent 可执行的技能文件。模型能力在趋同，Agent harness 也在趋同，那么差异化只能落在「你喂给它什么方法论」这一层。这对新人是个好消息：意味着你不需要懂最前沿的模型，也能做出有价值的贡献——把你自己领域的工作流写成 skill 就行。",
        "links": [
            ("obra/superpowers", "https://github.com/obra/superpowers"),
            ("mattpocock/skills", "https://github.com/mattpocock/skills"),
        ],
    },
    {
        "date": "2026-10-29",
        "title": "一个反直觉的观察：社区活跃度比 star 更能说明项目健康",
        "body": "算推荐分的时候我加了一个权重：fork 数 / star 数的比例。理由很简单——star 是「收藏」，fork 是「我打算动手用」。一个 50k star 但 fork 只有 500 的项目，多半是「听说过，收藏了，没用过」；一个 10k star 但 fork 有 2500 的项目，说明真的有人在拿它干活。实践中这个指标比 star 数更能区分「名气大」和「真有用」。当然也有反例——像 build-your-own-x 这种纯索引型项目，fork 少是正常的。所以这个指标得结合项目类型看，不能一刀切。",
        "links": [],
    },
    {
        "date": "2026-10-29",
        "title": "给自己立个规矩：每个项目都真的翻开 README",
        "body": "最初的版本我只想把 API 返回的数据格式化一下就上线。但那样的话，这个站就退化成了一个数字看板——star 数、排名、链接，全是别人已经有的信息，别人做得比我快。我决定每期至少挑几个项目真的把 README 读完，把「它到底在做什么」「为什么这样设计」「门槛在哪」写出来。写深度拆解的时候才发现，很多项目的 README 前三段就能看出作者的水平，而有些 star 极高的项目 README 写得很糟。这层信息是 API 给不了、榜单也给不了的——这才是这个站值得存在的地方。",
        "links": [],
    },
]


def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    # 1) 深度拆解：合并自动事实 + 人工判断
    for d in data.get("deep_dives", []):
        content = DEEP_CONTENT.get(d["name"])
        if content:
            d["summary"] = content["summary"]
            d["sections"] = content["sections"]
            d["verdict"] = content["verdict"]
            d["has_analysis"] = True
        else:
            # 没有人工文案的项目，生成一个基于事实的简版
            d["sections"] = [
                {
                    "title": "项目速览",
                    "paragraphs": [
                        d.get("summary") or "（该项目没有填写简介）",
                        f"最近一次代码提交在 {d.get('pushed_at', '未知')}，"
                        f"当前有 {fmt(d.get('open_issues'))} 个未关闭 issue，"
                        f"许可证为 {d.get('license') or '未声明'}。",
                    ],
                    "bullets": [],
                }
            ]
            d["verdict"] = (
                f"这是一个 star 数 {fmt(d.get('stars'))} 的项目，"
                f"fork {fmt(d.get('forks'))}。"
                + ("许可证清晰，适合上手试用。" if d.get("license") else
                   "注意：没有明确声明许可证，商用前需谨慎。")
            )
            d["has_analysis"] = False

        # 指标卡片
        metrics = [
            ("★ " + fmt(d.get("stars")), "Star"),
            ("⑂ " + fmt(d.get("forks")), "Fork"),
            ("⌀ " + fmt(d.get("score")), "推荐分"),
        ]
        if d.get("growth_30d") is not None:
            metrics.insert(1, ("+" + fmt(d["growth_30d"]), "30天新增"))
        if d.get("language"):
            metrics.append((d["language"], "主要语言"))
        if d.get("license"):
            metrics.append((d["license"], "许可证"))
        d["metrics"] = metrics

    # 2) 本期精选：优先选有真人工分析的，按分类轮换，避免全是同一类
    analyzed = [d for d in data.get("deep_dives", []) if d.get("has_analysis")]
    # 分类轮换：每个分类最多取 2 个，保证多样性
    by_cat = {}
    for d in analyzed:
        by_cat.setdefault(d.get("category", "other"), []).append(d)
    picks = []
    round_no = 0
    while len(picks) < 4 and round_no < 4:
        for cat, items in by_cat.items():
            if round_no < len(items):
                d = items[round_no]
                if d["name"] not in [p["full_name"] for p in picks]:
                    picks.append({
                        "full_name": d["name"], "url": d["url"],
                        "description": d.get("summary", ""),
                        "language": d.get("language"), "stars": d.get("stars", 0),
                        "growth_30d": d.get("growth_30d"),
                        "topics": d.get("topics", []), "score": d.get("score"),
                        "category": d.get("category", ""),
                        "badge": "🔍 已深读",
                        "note": "本期深度拆解",
                    })
        round_no += 1
    picks = picks[:4]
    data["hero_picks"] = picks

    # 3) 手记
    data["thoughts"] = THOUGHTS

    # 4) 分类说明
    data["category_notes"] = {
        "evergreen": "这一栏不看 star 总数（老牌项目几乎不涨，总数永远那几个），改看「近 30 天新增 star」——谁在悄悄上位，一眼就能看出来。未配置 token 时退化为「近 90 天提交数」，同样能看出谁还在高强度维护。",
        "hot_week": "最近 30 天内新建的仓库。star 数还不高，但增速吓人——这里最容易淘到未来的 stars。",
        "new_star": "三个月内冒头的一批。相比「本周最热」范围更广，能看到上升早期的样子。",
        "beginner": "有 good-first-issue 标签的项目，文档通常也更友好。第一次给开源提 PR 不知道从哪开始的话，看这里。",
        "fun": "不一定最有用，但一定有意思。有些项目纯粹是让人看着解压——这也是开源生态的一部分。",
        "learning": "系统性的学习路径。比起零散搜教程，跟着一条走完的收获要大得多。",
    }

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"深度拆解: {len(data['deep_dives'])} 个（其中 {len(picks)} 个进入精选）")
    print(f"手记: {len(data['thoughts'])} 条")
    print("文案注入完成")


if __name__ == "__main__":
    main()
