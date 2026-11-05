#!/usr/bin/env python3
"""SEO + GEO helpers that keep themselves up to date. Safe to run again.

1. Breadcrumbs: adds a BreadcrumbList (Home > page) JSON-LD block to every public page except the home page.
2. llms-full.txt: a long plain-text guide for AI search engines, built from guide-kb.json (what each tool is
   and how to use it), so it always matches what Bolt the guide says.
3. --dates: sets <lastmod> in sitemap.xml from the last git commit of each page (needs full git history,
   the workflow checks out with fetch-depth 0).

Usage: python3 tools/seo_enhance.py [--dates]
"""
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://geopolcoins.xyz/"
MARK = 'id="ld-crumbs"'


def public_pages():
    out = []
    for name in sorted(os.listdir(ROOT)):
        if not name.endswith(".html") or name.startswith("google") or name in ("index.html", "404.html", "offline.html"):
            continue
        s = open(os.path.join(ROOT, name), encoding="utf-8").read()
        if re.search(r'<meta[^>]+name="robots"[^>]+noindex', s, re.I):
            continue
        out.append(name)
    return out


def short_title(s):
    t = re.search(r"<title>(.*?)</title>", s, re.S)
    t = html.unescape(t.group(1).strip()) if t else ""
    t = re.split(r"\s+[|·]\s+|:\s", t)[0].strip()
    return t[:70]


def breadcrumbs():
    n = 0
    for name in public_pages():
        path = os.path.join(ROOT, name)
        s = open(path, encoding="utf-8").read()
        data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": short_title(s), "item": SITE + name}]}
        block = '<script type="application/ld+json" ' + MARK + '>' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"
        if MARK in s:
            s2 = re.sub(r'<script type="application/ld\+json" id="ld-crumbs">.*?</script>', lambda m: block, s, count=1, flags=re.S)
        else:
            s2 = s.replace("</head>", block + "\n</head>", 1)
        if s2 != s:
            open(path, "w", encoding="utf-8").write(s2)
            n += 1
    print(f"breadcrumbs: {n} pages updated")


def llms_full():
    kb = json.load(open(os.path.join(ROOT, "guide-kb.json"), encoding="utf-8"))
    head = open(os.path.join(ROOT, "llms.txt"), encoding="utf-8").read().split("\n## ")[0].rstrip()
    lines = [head, "", "This is the long version of https://geopolcoins.xyz/llms.txt: every tool and game, what it is and how to use it.", ""]
    groups = [("tool", "Tools"), ("game", "Games"), ("learn", "Learn"), ("business", "For businesses"), ("help", "Help and safety")]
    for kind, label in groups:
        items = [t for t in kb["topics"] if t["kind"] == kind]
        if not items:
            continue
        lines.append(f"## {label}")
        lines.append("")
        for t in items:
            url = t["url"] if t["url"].startswith("http") else SITE + t["url"].lstrip("/")
            lines.append(f"### {t['title']['en']}")
            lines.append(f"URL: {url}")
            lines.append(t["what"]["en"])
            lines.append("How to use it:")
            for i, st in enumerate(t["steps"]["en"], 1):
                lines.append(f"{i}. {st}")
            lines.append("")
    lines.append("## Official token facts")
    lines.append("")
    lines.append("Machine-readable: https://geopolcoins.xyz/token.json")
    lines.append("")
    open(os.path.join(ROOT, "llms-full.txt"), "w", encoding="utf-8").write("\n".join(lines))
    print("llms-full.txt written")


def sitemap_dates():
    path = os.path.join(ROOT, "sitemap.xml")
    s = open(path, encoding="utf-8").read()

    def last(name):
        try:
            d = subprocess.run(["git", "log", "-1", "--format=%cs", "--", name], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        except Exception:  # noqa: BLE001
            d = ""
        return d

    def fix(m):
        loc, rest = m.group(1), m.group(2)
        name = loc[len(SITE):] or "index.html"
        d = last(name)
        if d:
            rest = re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{d}</lastmod>", rest, count=1)
        return f"<url><loc>{loc}</loc>{rest}</url>"

    s2 = re.sub(r"<url><loc>([^<]+)</loc>(.*?)</url>", fix, s, flags=re.S)
    if s2 != s:
        open(path, "w", encoding="utf-8").write(s2)
    print("sitemap dates checked")


if __name__ == "__main__":
    breadcrumbs()
    llms_full()
    if "--dates" in sys.argv:
        sitemap_dates()
