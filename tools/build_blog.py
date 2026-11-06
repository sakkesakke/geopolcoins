#!/usr/bin/env python3
"""Build the blog: blog.html (index), blog-<slug>.html (articles) and blog-feed.xml (RSS).
Content lives in tools/blog_posts.py. Safe to run again; output is deterministic.
Pages live in the site root on purpose, so the SEO/security audits and IndexNow pick them up."""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blog_posts import POSTS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://geopolcoins.xyz/"
CSP = ("default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
       "font-src 'self'; connect-src 'self'; manifest-src 'self'; worker-src 'self'; frame-src 'none'; base-uri 'none'; form-action 'self'")
TAGC = {"Safety": "#ff6b6b", "AI": "#c8a8ff", "Learn": "#5fd3c6", "Business": "#ffb547", "Create": "#f3ecd9", "$MAIGA": "#ffb547"}
ORG = {"@type": "Organization", "name": "geopolcoins.xyz", "url": SITE, "logo": SITE + "logo.png"}

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    def link(m):
        txt, url = m.group(1), m.group(2)
        ext = url.startswith("http")
        return f'<a href="{html.escape(url)}"' + (' rel="noopener noreferrer" target="_blank"' if ext else "") + f">{txt}</a>"
    return re.sub(r"\[(.+?)\]\((\S+?)\)", link, t)

def plain(t):
    return re.sub(r"\[(.+?)\]\(\S+?\)", r"\1", t).replace("**", "")

def block(b):
    k, v = b
    if k == "p": return f"<p>{inline(v)}</p>"
    if k == "h2": return f"<h2>{inline(v)}</h2>"
    if k in ("ul", "ol"): return f"<{k}>" + "".join(f"<li>{inline(i)}</li>" for i in v) + f"</{k}>"
    if k == "quick": return f'<div class="quick"><b>Quick answer</b><p>{inline(v)}</p></div>'
    if k == "note": return f'<p class="note">{inline(v)}</p>'
    if k == "cta": return f'<p class="cta"><a class="btn" href="{html.escape(v[1])}">{html.escape(v[0])}</a></p>'
    raise ValueError(k)

CSS = """@font-face{font-family:"Jersey 10";src:url(/fonts/jersey-10.woff2) format("woff2");font-weight:400;font-display:swap}
:root{--night:#120f1e;--floor:#191427;--cab:#251c38;--line:rgba(241,235,224,.12);--text:#f1ebe0;--dim:#b3a9c4;--mute:#8f85a3;--amber:#ffb547;--cream:#f3ecd9;--teal:#5fd3c6;--red:#ff6b6b;--pix:"Jersey 10",ui-monospace,Consolas,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--night);color:var(--text);font:18px/1.7 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--amber)}a:focus-visible{outline:3px solid var(--teal);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:8px;top:-60px;background:var(--amber);color:#1a1206;padding:10px 14px;border-radius:8px;font-weight:800;z-index:5}.skip:focus{top:8px}
.top{max-width:1100px;margin:0 auto;padding:14px 16px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.brand{color:var(--text);text-decoration:none;font-weight:800;margin-right:auto}.brand b{color:var(--amber)}
.top nav a{color:var(--dim);text-decoration:none;font-size:15px;margin-left:12px}
.wrap{max-width:740px;margin:0 auto;padding:0 16px 40px}
.crumbs{font-size:14px;color:var(--mute);margin:8px 0 18px}.crumbs a{color:var(--dim)}
.tag{display:inline-block;font:400 18px/1 var(--pix);padding:4px 10px 2px;border-radius:7px;color:#1a1206}
h1{font:400 clamp(38px,6.5vw,58px)/1 var(--pix);margin:12px 0 10px;letter-spacing:0;text-wrap:balance}
.meta{color:var(--mute);font-size:14px;margin:0 0 22px}
h2{font:400 32px/1.1 var(--pix);margin:34px 0 8px;letter-spacing:0;color:var(--cream)}
p,li{color:#e4dcef}li{margin:4px 0}ul,ol{padding-left:22px}
.quick{background:var(--cab);border-left:5px solid var(--teal);border-radius:12px;padding:14px 18px;margin:0 0 22px}
.quick b{font:400 22px/1 var(--pix);color:var(--teal)}.quick p{margin:6px 0 0}
.note{border:1px dashed rgba(255,181,71,.5);border-radius:10px;padding:10px 14px;color:var(--cream);font-size:15.5px;background:rgba(255,181,71,.06)}
.btn{display:inline-block;background:var(--amber);color:#1a1206;text-decoration:none;font-weight:800;padding:12px 20px;border-radius:10px}
.cta{margin:28px 0}
.faq details{background:var(--cab);border-radius:10px;padding:10px 14px;margin:8px 0}.faq summary{cursor:pointer;font-weight:700}.faq p{margin:6px 0 2px;font-size:16.5px}
.more{display:grid;gap:10px;margin:14px 0 0;padding:0;list-style:none}
.card{display:block;background:var(--cab);border:1px solid var(--line);border-radius:14px;padding:16px 18px;text-decoration:none;color:var(--text)}
.card:hover{border-color:var(--amber)}.card h3{font:400 26px/1.1 var(--pix);margin:8px 0 6px;letter-spacing:0}.card p{margin:0;color:var(--dim);font-size:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;list-style:none;padding:0;margin:20px 0 0}
.lead{color:var(--dim);font-size:19px;margin:0 0 6px}
footer{border-top:1px solid var(--line);max-width:1100px;margin:30px auto 0;padding:18px 16px 40px;color:var(--mute);font-size:14px;display:flex;gap:14px;flex-wrap:wrap}footer a{color:var(--dim)}
@media (max-width:600px){body{font-size:17px}.top nav{width:100%}.top nav a{margin:0 12px 0 0}}"""

def head(title, desc, url, ld, ogtype="article"):
    lds = "".join(f'<script type="application/ld+json"{(" id=" + chr(34) + "ld-crumbs" + chr(34)) if d.get("@type") == "BreadcrumbList" else ""}>{json.dumps(d, ensure_ascii=False, separators=(",", ":"))}</script>\n' for d in ld)
    t, d = html.escape(title), html.escape(desc)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<link rel="alternate" type="application/rss+xml" title="geopolcoins.xyz blog" href="/blog-feed.xml">
<meta property="og:type" content="{ogtype}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#120f1e">
{lds}<style>
{CSS}
</style>
<link rel="stylesheet" href="/motion.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><a class="brand" href="/"><b>$MAIGA</b> · geopolcoins.xyz</a><nav aria-label="Main"><a href="/blog.html">Blog</a><a href="/radar.html">Radar</a><a href="/hq.html#checkup">Token Checkup</a><a href="/kronos.html">Kronos Lab</a></nav></header>
"""

FOOT = """<footer><a href="/">Home</a><a href="/blog.html">Blog</a><a href="/blog-feed.xml">RSS</a><a href="/privacy.html">Privacy</a><a href="/legal.html">Legal</a><span>Education and entertainment. Not financial advice.</span></footer>
<script src="/guide.js" defer></script>
</body>
</html>
"""

def date_h(d):
    import datetime
    return datetime.date.fromisoformat(d).strftime("%-d %B %Y")

def card(p, h="h3"):
    c = TAGC.get(p["tag"], "#ffb547")
    return (f'<a class="card" href="/blog-{p["slug"]}.html"><span class="tag" style="background:{c}">{html.escape(p["tag"])}</span>'
            f'<{h}>{html.escape(p["title"])}</{h}><p>{html.escape(p["desc"])}</p></a>')

def article(p, i):
    url = f"{SITE}blog-{p['slug']}.html"
    words = sum(len(plain(v if isinstance(v, str) else " ".join(v) if isinstance(v, list) else " ".join(v)).split()) for k, v in p["body"])
    ld = [{"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["desc"], "datePublished": p["date"],
           "dateModified": p.get("updated", p["date"]), "author": ORG, "publisher": ORG, "mainEntityOfPage": url, "image": SITE + "og-image.jpg",
           "inLanguage": "en", "wordCount": words, "about": p["tool"][0], "isAccessibleForFree": True},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
              {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "blog.html"},
              {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]}]
    if p.get("faq"):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]})
    c = TAGC.get(p["tag"], "#ffb547")
    out = [head(p["title"], p["desc"], url, ld), '<main id="main" class="wrap">',
           '<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › <a href="/blog.html">Blog</a></nav>',
           f'<article><span class="tag" style="background:{c}">{html.escape(p["tag"])}</span><h1>{html.escape(p["title"])}</h1>',
           f'<p class="meta">{date_h(p["date"])} · {max(1, round(words / 200))} min read · Tool: <a href="{html.escape(p["tool"][1])}">{html.escape(p["tool"][0])}</a></p>']
    out += [block(b) for b in p["body"]]
    if p.get("faq"):
        out.append('<h2>Questions</h2><div class="faq">' + "".join(
            f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in p["faq"]) + "</div>")
    out.append("</article>")
    others = [q for q in POSTS if q is not p]
    rel = [q for q in others if q["tag"] == p["tag"]][:2]
    rel += [q for q in others if q not in rel][: 3 - len(rel)]
    out.append('<h2>Read next</h2><ul class="more">' + "".join(f"<li>{card(q)}</li>" for q in rel) + "</ul>")
    out.append("</main>")
    out.append(FOOT)
    return "\n".join(out)

def index():
    url = SITE + "blog.html"
    ld = [{"@context": "https://schema.org", "@type": "Blog", "name": "geopolcoins.xyz blog", "url": url, "inLanguage": "en", "publisher": ORG,
           "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}blog-{p['slug']}.html", "datePublished": p["date"]} for p in POSTS]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
              {"@type": "ListItem", "position": 2, "name": "Blog", "item": url}]}]
    out = [head("Blog: crypto safety, AI and free tools explained", "Plain guides on spotting Solana scams, reading charts, AI and crypto, blockchains, free AI bots for small business, and the $MAIGA meme coin.", url, ld, "website"),
           '<main id="main" class="wrap" style="max-width:1100px">',
           '<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › Blog</nav>',
           '<h1>The <span style="color:var(--amber)">blog</span></h1>',
           '<p class="lead">Short, honest guides: how to spot scams, read a chart, test AI claims and use our free tools. No hype, no price talk.</p>',
           '<ul class="grid">' + "".join(f"<li>{card(p, 'h2')}</li>" for p in POSTS) + "</ul>", "</main>", FOOT]
    return "\n".join(out)

def feed():
    import email.utils, datetime
    items = []
    for p in POSTS:
        dt = datetime.datetime.fromisoformat(p["date"] + "T09:00:00+00:00")
        items.append(f"<item><title>{html.escape(p['title'])}</title><link>{SITE}blog-{p['slug']}.html</link><guid>{SITE}blog-{p['slug']}.html</guid>"
                     f"<pubDate>{email.utils.format_datetime(dt)}</pubDate><description>{html.escape(p['desc'])}</description></item>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>geopolcoins.xyz blog</title>'
            f"<link>{SITE}blog.html</link><description>Crypto safety, AI and free tools explained.</description><language>en</language>"
            + "".join(items) + "</channel></rss>\n")

def main():
    seen = set()
    for i, p in enumerate(POSTS):
        assert p["slug"] not in seen and re.fullmatch(r"[a-z0-9-]+", p["slug"]); seen.add(p["slug"])
        assert len(p["desc"]) <= 160, (p["slug"], len(p["desc"]))
        assert len(p["title"]) <= 70, (p["slug"], len(p["title"]))
        open(os.path.join(ROOT, f"blog-{p['slug']}.html"), "w", encoding="utf-8").write(article(p, i))
    open(os.path.join(ROOT, "blog.html"), "w", encoding="utf-8").write(index())
    open(os.path.join(ROOT, "blog-feed.xml"), "w", encoding="utf-8").write(feed())
    # sitemap: add any missing blog URLs
    sm = os.path.join(ROOT, "sitemap.xml"); s = open(sm, encoding="utf-8").read()
    add = ""
    for name in ["blog.html"] + [f"blog-{p['slug']}.html" for p in POSTS]:
        if f"{SITE}{name}</loc>" not in s:
            add += f"  <url><loc>{SITE}{name}</loc><lastmod>{POSTS[0]['date']}</lastmod><changefreq>monthly</changefreq><priority>{'0.8' if name == 'blog.html' else '0.6'}</priority></url>\n"
    if add:
        s = s.replace("</urlset>", add + "</urlset>"); open(sm, "w", encoding="utf-8").write(s)
    print(f"blog: {len(POSTS)} posts, index, feed; sitemap +{add.count('<url>')}")

if __name__ == "__main__":
    main()
