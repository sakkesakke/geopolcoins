#!/usr/bin/env python3
"""Build guide-kb.json: everything Bolt the guide knows about the site.

Sources:
- tools/guide_topics.json: hand-written "what it is + how to use it" per tool/game (EN/NL/FR).
- every public page (no noindex): title, description and headings, read straight from the HTML,
  so new pages are known automatically. A workflow re-runs this when pages change.

Usage: python3 tools/build_guide_kb.py   (writes guide-kb.json in the repo root)
"""
import glob
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"google9970ace9218804f6.html", "404.html", "offline.html"}


def clean(s):
    s = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def page_info(path):
    raw = open(path, encoding="utf-8").read()
    if re.search(r'<meta[^>]+name="robots"[^>]+noindex', raw, re.I):
        return None
    title = clean((re.search(r"<title>(.*?)</title>", raw, re.S) or [None, ""])[1])
    desc = (re.search(r'<meta name="description" content="([^"]*)"', raw) or [None, ""])[1]
    lang = (re.search(r'<html[^>]*lang="([a-z]{2})', raw) or [None, "en"])[1]
    heads = [clean(h) for h in re.findall(r"<h[1-3][^>]*>(.*?)</h[1-3]>", raw, re.S)]
    heads = [h for h in heads if 2 < len(h) < 90]
    seen, uniq = set(), []
    for h in heads:
        if h.lower() not in seen:
            seen.add(h.lower())
            uniq.append(h)
    return {"url": os.path.basename(path), "title": title, "desc": html.unescape(desc), "lang": lang,
            "text": " · ".join(uniq)[:600]}


def main():
    topics = json.load(open(os.path.join(ROOT, "tools", "guide_topics.json"), encoding="utf-8"))
    pages = []
    for p in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        if os.path.basename(p) in SKIP:
            continue
        info = page_info(p)
        if info and info["title"]:
            pages.append(info)
    by_url = {p["url"]: p for p in pages}
    for t in topics:
        page = by_url.get(t["url"].split("#")[0].lstrip("/") or "index.html")
        t["text"] = page["text"] if page else ""
        for k in ("en", "nl", "fr"):
            for key in ("title", "what", "cta"):
                assert t[key].get(k), f"{t['id']} misses {key}.{k}"
            assert t["steps"].get(k), f"{t['id']} misses steps.{k}"
    covered = {t["url"].split("#")[0].lstrip("/") or "index.html" for t in topics}
    covered |= {t.get("url_nl", "") for t in topics} | {t.get("url_fr", "") for t in topics}
    extra = [p for p in pages if p["url"] not in covered]
    out = {"v": 1, "topics": topics, "pages": extra}
    dst = os.path.join(ROOT, "guide-kb.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"guide-kb.json: {len(topics)} topics, {len(extra)} extra pages, {os.path.getsize(dst)} bytes")


if __name__ == "__main__":
    main()
