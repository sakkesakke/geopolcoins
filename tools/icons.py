#!/usr/bin/env python3
"""Line icons instead of emoji (unslop pass 3). Safe to run again.

Inlines a small SVG sprite with only the Lucide icons a page uses, right after <body>, and adds the
.i icon style. Icons: Lucide (https://lucide.dev), ISC License, (c) Lucide Icons and Contributors.

Usage: python3 tools/icons.py LUCIDE_ICON_DIR page.html [page.html ...]
In the page write <svg class="i" aria-hidden="true"><use href="#i-NAME"></use></svg>.
"""
import os
import re
import sys

STYLE = (".i{width:1.15em;height:1.15em;flex:none;vertical-align:-.2em;fill:none;stroke:currentColor;"
         "stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round}")


def symbol(icon_dir, name):
    raw = open(os.path.join(icon_dir, name + ".svg"), encoding="utf-8").read()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", raw, re.S).group(1)
    inner = re.sub(r"<!--.*?-->", "", inner, flags=re.S)
    inner = re.sub(r"\s+", " ", inner).replace("> <", "><").strip()
    return f'<symbol id="i-{name}" viewBox="0 0 24 24">{inner}</symbol>'


def apply(icon_dir, path):
    s = open(path, encoding="utf-8").read()
    s = re.sub(r'<svg id="lucide-sprite".*?</svg>\n?', "", s, flags=re.S)
    names = sorted(set(re.findall(r'<use href="#i-([a-z0-9-]+)"', s)))
    if not names:
        return 0
    sprite = ('<svg id="lucide-sprite" width="0" height="0" style="position:absolute" aria-hidden="true">'
              "<!-- Lucide icons, ISC License, https://lucide.dev -->" + "".join(symbol(icon_dir, n) for n in names) + "</svg>\n")
    s = re.sub(r"(<body[^>]*>\n?)", lambda m: m.group(1) + sprite, s, count=1)
    if ".i{width:1.15em" not in s:
        s = s.replace("</style>", STYLE + "\n</style>", 1)
    open(path, "w", encoding="utf-8").write(s)
    return len(names)


if __name__ == "__main__":
    d = sys.argv[1]
    for p in sys.argv[2:]:
        print(p, apply(d, p), "icons")
