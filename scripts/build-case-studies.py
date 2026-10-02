"""Build static, bilingual walkthroughs from reviewed copy and frozen case metadata."""
from __future__ import annotations
import argparse
from collections import Counter
import html
import json
from pathlib import Path
import re
from urllib.parse import quote

SITE = Path(__file__).resolve().parents[1]
WEB = "https://artist-coding.github.io/"
REPO = "https://github.com/artist-coding/harnesssafe/"
FAMILIES = {
    "F1": ("持久记忆", "Persistent memory", 72, "旧经验如何变成新决定的依据。", "How saved experience shapes a new decision."),
    "F2": ("可复用技能", "Reusable skills", 84, "一次技能调用，如何影响下一次执行。", "How one skill invocation affects the next."),
    "F3": ("工具 / MCP", "Tools / MCP", 70, "工具返回内容与缓存如何跨过重启。", "How tool output and cached metadata survive a restart."),
    "T2": ("记忆 → 技能", "Memory → skill", 36, "项目记忆如何转化为可执行的操作步骤。", "How project memory becomes executable procedure."),
    "T3-S": ("子代理委派", "Subagent delegation", 30, "子代理的交接内容如何影响主代理。", "How a delegated handoff influences the main agent."),
    "T3-C": ("压缩与恢复", "Compaction & resume", 30, "旧指令如何随摘要或恢复上下文再次出现。", "How old instructions return through summaries or resumed context."),
    "T3-A": ("共享产物", "Shared artifacts", 6, "文档与模板如何把风险带入下一次任务。", "How documents and templates carry risk into a later task."),
}
e = html.escape

def bi(zh, en):
    return '<span class="zh">' + e(zh) + '</span><span class="en">' + e(en) + '</span>'

def copy(value):
    return bi(value["zh"], value["en"])

def family_file(family):
    return family.lower() + ".html"

def source(case, filename="case_meta.json"):
    return REPO + "blob/main/runs/" + quote(case["path"] + "/" + filename, safe="/")

def link(case, prefix=""):
    return prefix + "case-studies/" + family_file(case["family"]) + "#" + case["slug"]

def replace_block(text, name, content, before):
    start, end = "<!-- " + name + ":start -->", "<!-- " + name + ":end -->"
    block = start + "\n" + content.strip() + "\n" + end + "\n"
    if start in text:
        return re.sub(re.escape(start) + r".*?" + re.escape(end) + r"\n?", lambda _: block, text, flags=re.S)
    if before not in text:
        raise ValueError("Missing insertion point: " + before)
    return text.replace(before, block + "\n" + before, 1)

def navigation(text):
    if 'href="case-studies.html"' not in text.split("</header>")[0]:
        needle = '      <a href="index.html#results">'
        text = text.replace(needle, '      <a href="case-studies.html">' + bi("精选案例", "Cases") + '</a>\n' + needle, 1)
    return text

def page(template, title, description, path, main):
    head = template.split('<main id="main"')[0]
    tail = template[template.index('<footer class="footer">'):]
    head = re.sub(r"<title>.*?</title>", "<title>" + e(title) + "</title>", head)
    for attr, key, content in [
        ("name", "description", description),
        ("property", "og:title", title),
        ("property", "og:description", description),
        ("property", "og:url", WEB + path),
    ]:
        head = re.sub(r'<meta ' + attr + '="' + key + r'" content="[^"]*">', '<meta ' + attr + '="' + key + '" content="' + e(content, quote=True) + '">', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="' + WEB + path + '">', head)
    if "/" in path:
        # Only chrome assets and home links change depth; main content uses explicit links.
        def up(match):
            return match.group(1) + "../" + match.group(2)
        head = re.sub(r'((?:href|src)=")(assets/|index.html|case-studies.html)', up, head)
        tail = re.sub(r'((?:href|src)=")(assets/|index.html|case-studies.html)', up, tail)
    return head + '<main id="main" class="wrap stories-page">\n' + main + "\n</main>" + tail

def disclosure(case):
    fields = case["_index"]
    labels = [("entry", "入口", "Entry"), ("carrier", "载体", "Carrier"),
              ("boundary", "边界", "Boundary"), ("trigger", "触发", "Trigger"),
              ("violation", "目标违规", "Target violation")]
    rows = "".join("<dt>" + bi(zh, en) + "</dt><dd><code>" + e(str(fields[key])) + "</code></dd>" for key, zh, en in labels)
    oracles = "".join("<li><code>" + e(value) + "</code></li>" for value in case["_meta"].get("oracles", []))
    sources = '<li><a href="' + source(case) + '">case_meta.json ↗</a></li>'
    sources += "".join('<li><a href="' + source(case, name) + '">' + e(name) + ' ↗</a></li>' for name in case["source_files"])
    return '<details class="study-source"><summary>' + bi("查看原始定义与检查信号", "Inspect source definitions and oracle names") + '</summary><div class="study-source-body"><p class="source-id"><code>' + e(case["case_id"]) + '</code></p><dl>' + rows + '</dl><h4>' + bi("元数据中声明的检查信号", "Oracles declared in the metadata") + '</h4><ul class="oracle-list">' + oracles + '</ul><h4>' + bi("原始文件", "Source files") + '</h4><ul class="source-files">' + sources + '</ul></div></details>'

def study(case, number):
    stages = [("污染入口", "Entry"), ("如何留存", "Persistence"), ("后续触发", "Later trigger")]
    steps = "".join('<li><span class="step-number">0' + str(i + 1) + '</span><h4>' + bi(*stages[i]) + '</h4><p>' + copy(step) + '</p></li>' for i, step in enumerate(case["steps"]))
    return '<article class="case-study" id="' + case["slug"] + '"><header class="study-header"><p class="eyebrow">' + case["family"] + ' / CASE 0' + str(number) + '</p><h2>' + copy(case["title"]) + '</h2><p class="study-hook">' + copy(case["hook"]) + '</p></header><div class="study-task"><h3>' + bi("正常任务", "The legitimate task") + '</h3><p>' + copy(case["task"]) + '</p></div><h3 class="path-heading">' + bi("案例中的风险路径", "The risk path in this case") + '</h3><ol class="study-path">' + steps + '</ol><div class="study-outcomes"><section><h3>' + bi("正常行为应是什么", "Expected behavior") + '</h3><p>' + copy(case["safe"]) + '</p></section><section><h3>' + bi("用什么证据判定", "Evidence to inspect") + '</h3><p>' + copy(case["watch"]) + '</p></section></div>' + disclosure(case) + '</article>'

def note():
    return '<p class="study-note">' + bi("这里展示冻结案例的机制设计，不代表某个当前版本已发生违规。是否触发，需要检查一次运行的实际证据；文中的 canary（测试标记）、marker 文件与回调端点均为实验夹具。", "These walkthroughs explain frozen case designs, not observed violations in a current release. Outcomes require evidence from an actual run. Canaries, marker files, and callback endpoints are test fixtures.") + '</p>'

def teaser(case):
    chain = "".join("<li>" + bi(zh, en) + "</li>" for zh, en in zip(case["preview_chain"]["zh"], case["preview_chain"]["en"]))
    return '<a class="story-teaser" href="' + link(case) + '"><span class="eyebrow">' + case["family"] + ' / CASE STUDY</span><h3>' + copy(case["title"]) + '</h3><p>' + copy(case["hook"]) + '</p><ol class="teaser-chain">' + chain + '</ol><span class="text-link">' + bi("展开这条路径", "Follow this case") + ' →</span></a>'

def build(root, update_readme=False):
    cases = json.loads((SITE / "content/case-studies.json").read_text(encoding="utf-8"))["cases"]
    inventory = {case["id"]: case for case in json.loads((SITE / "assets/cases.json").read_text(encoding="utf-8"))["cases"]}
    assert len(cases) == 14 and len({c["case_id"] for c in cases}) == 14
    assert len({c["slug"] for c in cases}) == 14
    assert Counter(c["family"] for c in cases) == Counter({family: 2 for family in FAMILIES})
    for case in cases:
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", case["slug"])
        record = inventory[case["case_id"]]
        assert record["family"] == case["family"] and record["path"] == case["path"]
        case_root = (root / "runs" / case["path"]).resolve()
        case_root.relative_to((root / "runs").resolve())
        case["_meta"] = json.loads((case_root / "case_meta.json").read_text(encoding="utf-8-sig"))
        assert case["_meta"]["case_id"] == case["case_id"]
        case["_index"] = record
        assert len(case["steps"]) == 3
        for name in case["source_files"]:
            file = (case_root / name).resolve()
            file.relative_to(case_root)
            assert file.is_file(), file
    index_path = SITE / "index.html"
    index = navigation(index_path.read_text(encoding="utf-8"))
    index = index.replace('class="text-link" href="cases.html"><span class="zh">浏览案例', 'class="text-link" href="case-studies.html"><span class="zh">浏览案例')
    for family in FAMILIES:
        index = index.replace('class="family-row" href="cases.html#' + family + '"', 'class="family-row" href="case-studies/' + family_file(family) + '"')
    featured = [next(c for c in cases if c["slug"] == slug) for slug in ["health-monitor-cache", "cached-schema-token", "summary-marker"]]
    preview = '<section class="section wrap" id="featured-cases"><div class="section-heading"><div><p class="eyebrow">CASE STUDIES</p><h2>' + bi("从一个正常任务，看到风险如何回来。", "Start with a normal task. See how risk returns.") + '</h2></div><p>' + bi("挑选 14 个案例，逐步展示污染入口、留存过程与后续触发。每类两个，均可追溯到原始定义。", "Fourteen curated cases trace entry, persistence, and later triggers. Two per family, each linked to its source definition.") + '</p></div><div class="story-teasers">' + "".join(teaser(c) for c in featured) + '</div><div class="stories-cta"><a class="button primary" href="case-studies.html">' + bi("按类别阅读全部精选案例", "Explore all curated cases") + ' →</a><a class="text-link" href="cases.html">' + bi("检索全部 328 个案例", "Search all 328 cases") + ' ↗</a></div><p class="small-note">' + bi("以下展示案例设计；具体结果以实际运行证据为准。", "These are case designs; outcomes depend on evidence from an actual run.") + '</p></section>'
    index = replace_block(index, "featured-cases", preview, '<section class="section wrap" id="results">')
    index_path.write_text(index, encoding="utf-8", newline="\n")
    explorer_path = SITE / "cases.html"
    explorer = navigation(explorer_path.read_text(encoding="utf-8"))
    explorer = replace_block(explorer, "curated-link", '<aside class="explorer-intro"><p>' + bi("先从具体场景理解这些机制。", "Start with a concrete walkthrough.") + '</p><a class="text-link" href="case-studies.html">' + bi("阅读 14 个精选案例", "Read 14 curated cases") + ' →</a></aside>', '<section aria-label="Case filters"')
    explorer_path.write_text(explorer, encoding="utf-8", newline="\n")

    gallery = '<div class="stories-heading"><p class="eyebrow"><a href="index.html">HarnessSafe</a> / CASE STUDIES</p><h1>' + bi("风险如何留存，如何再次触发。", "How risk persists. How it returns.") + '</h1><p>' + bi("从七类机制中各选两个案例。先看正常任务，再沿着污染入口、持久载体与后续触发，理解一条完整的风险路径。", "Two cases from each of seven families. Start with the legitimate task, then trace the entry, persistent carrier, and later trigger.") + '</p><div class="stories-stats"><span><strong>14</strong> ' + bi("精选案例", "walkthroughs") + '</span><span><strong>7</strong> ' + bi("案例类别", "families") + '</span><a href="cases.html">' + bi("浏览完整的 328 个案例", "Browse all 328 cases") + ' ↗</a></div></div>' + note() + '<div class="family-gallery">'
    for family, (zh, en, total, desc_zh, desc_en) in FAMILIES.items():
        group = [c for c in cases if c["family"] == family]
        target = "case-studies/" + family_file(family)
        gallery += '<section class="family-gallery-card"><div class="family-card-top"><span class="family-code">' + family + '</span><span>' + bi("全量 " + str(total) + " 个", str(total) + " in full set") + '</span></div><h2><a href="' + target + '">' + bi(zh, en) + '</a></h2><p>' + bi(desc_zh, desc_en) + '</p><ul>' + "".join('<li><a href="' + link(c) + '">' + copy(c["title"]) + '<span aria-hidden="true">↗</span></a></li>' for c in group) + '</ul><a class="text-link" href="' + target + '">' + bi("阅读这类案例", "Explore this family") + ' →</a></section>'
    gallery += '</div><div class="stories-cta"><a class="button" href="cases.html">' + bi("检索全部冻结案例", "Search the full frozen benchmark") + ' →</a><a class="text-link" href="' + REPO + '#quickstart">' + bi("开始复现实验", "Start an experiment") + ' ↗</a></div>'
    (SITE / "case-studies.html").write_text(page(index, "Case Studies — HarnessSafe", "Fourteen concrete walkthroughs across seven HarnessSafe carrier families, with source definitions and evidence criteria.", "case-studies.html", gallery), encoding="utf-8", newline="\n")
    (SITE / "case-studies").mkdir(exist_ok=True)
    for family, (zh, en, total, desc_zh, desc_en) in FAMILIES.items():
        group = [c for c in cases if c["family"] == family]
        main = '<div class="stories-heading"><p class="eyebrow"><a href="../case-studies.html">' + bi("精选案例", "Case studies") + '</a> / ' + family + '</p><h1>' + bi(zh, en) + '</h1><p>' + bi(desc_zh, desc_en) + '</p><div class="stories-stats"><span><strong>2</strong> ' + bi("精选案例", "walkthroughs") + '</span><a href="../cases.html#' + family + '">' + bi("检索本类全部 " + str(total) + " 个案例", "Search all " + str(total) + " cases in this family") + ' ↗</a></div></div>'
        main += '<nav class="family-tabs" aria-label="Case families">' + "".join('<a href="' + family_file(f) + '"' + (' aria-current="page"' if f == family else '') + '>' + f + ' <span>' + bi(v[0], v[1]) + '</span></a>' for f, v in FAMILIES.items()) + '</nav>' + note()
        main += '<nav class="study-jumps" aria-label="On this page">' + "".join('<a href="#' + c["slug"] + '"><span>0' + str(i + 1) + '</span>' + copy(c["title"]) + ' ↓</a>' for i, c in enumerate(group)) + '</nav>'
        main += "".join(study(c, i + 1) for i, c in enumerate(group))
        main += '<div class="stories-cta"><a class="button" href="../case-studies.html">← ' + bi("查看其他类别", "All case families") + '</a><a class="text-link" href="../cases.html#' + family + '">' + bi("继续检索本类全部案例", "Search every case in this family") + ' →</a></div>'
        path = "case-studies/" + family_file(family)
        (SITE / path).write_text(page(index, family + " · " + en + " — HarnessSafe", "Two curated " + en.lower() + " cases: legitimate tasks, persistence paths, and evidence criteria.", path, main), encoding="utf-8", newline="\n")
    if update_readme:
        featured = [next(c for c in cases if c["slug"] == slug) for slug in ["persistent-consent", "health-monitor-cache", "cached-schema-token", "summary-marker"]]
        section = '<a id="featured-cases"></a>\n\n## 精选案例\n\n以下展示冻结案例的机制设计；是否触发，以一次运行的实际证据判定。文中的 canary、marker 与回调端点均为实验夹具。\n'
        for i, c in enumerate(featured):
            section += "\n### " + str(i + 1) + ". " + c["family"] + " · " + c["title"]["zh"] + "\n\n**正常任务：**" + c["task"]["zh"] + "\n\n**风险路径：**" + " → ".join(c["preview_chain"]["zh"]) + "。\n\n" + c["steps"][0]["zh"] + c["steps"][1]["zh"] + c["steps"][2]["zh"] + "\n\n**判定依据：**" + c["watch"]["zh"] + "\n\n[查看完整案例](" + WEB + link(c) + ") · [原始定义](runs/" + c["path"] + "/case_meta.json)\n"
        section += "\n[按七类阅读全部 14 个精选案例](" + WEB + "case-studies.html) · [检索全部 328 个案例](" + WEB + "cases.html)\n"
        readme_path = root / "README.md"
        readme = readme_path.read_text(encoding="utf-8")
        if 'href="#featured-cases"' not in readme:
            readme = readme.replace('  <a href="#quickstart">', '  <a href="#featured-cases">精选案例</a> ·\n  <a href="#quickstart">', 1)
        readme = replace_block(readme, "featured-cases", section, '<a id="quickstart"></a>')
        readme_path.write_text(readme, encoding="utf-8", newline="\n")
    print("Validated 14 source cases; built gallery, 7 family pages, homepage previews" + (" and README." if update_readme else "."))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark-root", type=Path, required=True)
    parser.add_argument("--update-readme", action="store_true", help="Also replace the curated section in the benchmark README.")
    args = parser.parse_args()
    build(args.benchmark_root.resolve(), args.update_readme)
