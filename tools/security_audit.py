#!/usr/bin/env python3
"""Small security checks for every page. Runs in CI next to the SEO audit.

Fails when a page:
- has no Content-Security-Policy meta tag (or allows 'unsafe-eval'),
- opens a link in a new tab without rel="noopener",
- loads a script over plain http,
- contains something that looks like a secret key.
Usage: python3 tools/security_audit.py
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"google9970ace9218804f6.html"}
SECRET = re.compile(r"(sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{32,}|xkeysib-[a-f0-9]{20,}|ghp_[A-Za-z0-9]{30,}|eyJhbGciOi[A-Za-z0-9_.-]{80,}service_role)")


def main():
    problems = []
    pages = [p for p in sorted(glob.glob(os.path.join(ROOT, "*.html"))) if os.path.basename(p) not in SKIP]
    for path in pages:
        name = os.path.basename(path)
        s = open(path, encoding="utf-8").read()
        m = re.search(r'http-equiv="Content-Security-Policy" content="([^"]*)"', s)
        if not m:
            problems.append(f"{name}: no Content-Security-Policy")
        else:
            csp = m.group(1)
            if "unsafe-eval" in csp:
                problems.append(f"{name}: CSP allows unsafe-eval")
            for d in ("default-src", "base-uri"):
                if d not in csp:
                    problems.append(f"{name}: CSP misses {d}")
        for a in re.findall(r"<a\b[^>]*target=\"_blank\"[^>]*>", s):
            if "noopener" not in a:
                problems.append(f"{name}: target=_blank without rel=noopener: {a[:80]}")
        if re.search(r'<script[^>]+src="http://', s):
            problems.append(f"{name}: script over plain http")
        if SECRET.search(s):
            problems.append(f"{name}: looks like a secret key")
    for p in problems:
        print(p)
    print(f"-- {len(pages)} pages, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
