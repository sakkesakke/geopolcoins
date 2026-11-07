#!/usr/bin/env python3
"""Growth machine for geopolcoins.xyz (run by .github/workflows/growth.yml).

  growth.py sample --data DIR    take a snapshot of the trending Solana pools (public GeckoTerminal data)
  growth.py weekly --data DIR    build this week's post kit (social/), report.html and the history file

Facts, not signals: we only count public red flags across many pools and never name or rate one token.
No secrets: the Supabase key used for the Language War is the public, read-only publishable key.
"""
import argparse, datetime as dt, glob, html, io, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GT = "https://api.geckoterminal.com/api/v2/networks/solana"
SB = "https://zslzbfbqrtfpvgbjhssd.supabase.co"
SB_KEY = "sb_publishable_90hLwzv3xb0aZmPtaHKZag_1hKkG0EN"  # public by design (same as on every page)
TEAM_NAMES = {"en": "English", "nl": "Nederlands", "fr": "Français", "es": "Español", "pt": "Português",
              "de": "Deutsch", "tr": "Türkçe", "id": "Bahasa Indonesia", "vi": "Tiếng Việt", "ar": "العربية"}
TEAM_EN = {"en": "English", "nl": "Dutch", "fr": "French", "es": "Spanish", "pt": "Portuguese", "de": "German", "tr": "Turkish", "id": "Indonesian", "vi": "Vietnamese", "ar": "Arabic"}  # pixel font has no accents/Arabic
TEAM_FLAGS = {"en": "🇬🇧", "nl": "🇳🇱", "fr": "🇫🇷", "es": "🇪🇸", "pt": "🇧🇷", "de": "🇩🇪", "tr": "🇹🇷", "id": "🇮🇩", "vi": "🇻🇳", "ar": "🌍"}


def get_json(url, headers=None, body=None):
    req = urllib.request.Request(url, data=body, headers={"Accept": "application/json", "User-Agent": "geopolcoins-growth/1.0", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def num(x):
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def week_id(d=None):
    d = d or dt.datetime.now(dt.timezone.utc)
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


# ---------------------------------------------------------------- 1) snapshot
def flags_of(a):
    """Same rules as the MAIGA Radar (radar.html)."""
    f = []
    liq = num(a.get("reserve_in_usd"))
    t = (a.get("transactions") or {}).get("h24") or {}
    b, s = num(t.get("buys")) or 0, num(t.get("sells")) or 0
    vol = num((a.get("volume_usd") or {}).get("h24"))
    ch = num((a.get("price_change_percentage") or {}).get("h24"))
    if liq is not None and liq < 10000: f.append("thin")
    if b >= 10 and s == 0: f.append("nosell")
    if liq and vol is not None and vol > liq * 50: f.append("vol")
    if ch is not None and ch >= 300: f.append("pump")
    if ch is not None and ch <= -60: f.append("crash")
    return f


def sample(data_dir):
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, f"redflags-{week_id()}.json")
    store = json.load(open(path)) if os.path.exists(path) else {"pools": {}}
    j = get_json(GT + "/trending_pools?page=1")
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes")
    n = 0
    for p in j.get("data") or []:
        a = p.get("attributes") or {}
        addr = str(a.get("address") or p.get("id") or "")[:64]
        if not addr:
            continue
        store["pools"][addr] = {"seen": now, "liq": num(a.get("reserve_in_usd")), "flags": flags_of(a)}
        n += 1
    json.dump(store, open(path, "w"), separators=(",", ":"))
    print(f"sampled {n} trending pools -> {path} ({len(store['pools'])} this week)")


# ---------------------------------------------------------------- 2) weekly kit
def stats_for(data_dir, wk):
    path = os.path.join(data_dir, f"redflags-{wk}.json")
    pools = (json.load(open(path)) if os.path.exists(path) else {"pools": {}})["pools"]
    n = len(pools)
    def pct(fn):
        return round(100 * sum(1 for p in pools.values() if fn(p)) / n) if n else 0
    return {"week": wk, "pools": n,
            "any": pct(lambda p: any(f in ("thin", "nosell") for f in p["flags"])),
            "thin": pct(lambda p: "thin" in p["flags"]), "nosell": pct(lambda p: "nosell" in p["flags"]),
            "vol": pct(lambda p: "vol" in p["flags"]), "pump": pct(lambda p: "pump" in p["flags"]),
            "crash": pct(lambda p: "crash" in p["flags"])}


def language_war():
    try:
        rows = get_json(SB + "/rest/v1/rpc/raid_teams", {"apikey": SB_KEY, "Content-Type": "application/json"}, b"{}")
        return [r for r in rows if r.get("team") in TEAM_NAMES][:10]
    except Exception as e:  # the kit still works without it
        print("language war unavailable:", e)
        return []


def blog_tip(wk):
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from blog_posts import POSTS  # noqa: E402
    posts = [p for p in POSTS if p["tag"] != "$MAIGA"]  # tips are about tools and safety, never about the coin
    p = posts[int(wk.split("W")[1]) % len(posts)]
    quick = next((t for k, t in p["body"] if k == "quick"), p["desc"])
    return {"title": p["title"], "quick": quick, "url": f"https://geopolcoins.xyz/blog-{p['slug']}.html"}


def fit(text, limit=270):
    """X counts every link as 23 characters. Shorten the longest paragraph without a link until it fits."""
    import re
    count = lambda t: len(re.sub(r"https?://\S+", "x" * 23, t))
    parts = text.split("\n\n")
    while count("\n\n".join(parts)) > limit:
        i = max((k for k, p in enumerate(parts) if "http" not in p), key=lambda k: len(parts[k]), default=None)
        if i is None or len(parts[i]) < 20:
            break
        parts[i] = parts[i][:-12].rsplit(" ", 1)[0] + "…"
    return "\n\n".join(parts)


# ---------- images (1600 x 900, the arcade style of the site)
def fonts():
    from PIL import ImageFont
    from fontTools.ttLib import TTFont
    ttf = os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "jersey-10.ttf")
    if not os.path.exists(ttf):
        f = TTFont(os.path.join(ROOT, "fonts", "jersey-10.woff2")); f.flavor = None; f.save(ttf)
    sans = next((p for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"] if os.path.exists(p)), None)
    return (lambda s: ImageFont.truetype(ttf, s)), (lambda s: ImageFont.truetype(sans, s) if sans else ImageFont.load_default())


def canvas(title, accent):
    from PIL import Image, ImageDraw
    W, H = 1600, 900
    im = Image.new("RGB", (W, H), (18, 15, 30)); d = ImageDraw.Draw(im)
    for x in range(0, W, 48): d.line([(x, 0), (x, H)], fill=(14, 11, 24), width=2)
    PIX, SANS = fonts()
    d.rounded_rectangle((60, 54, 60 + d.textlength(title, font=PIX(78)) + 48, 150), 14, fill=accent)
    d.text((84, 60), title, font=PIX(78), fill=(26, 18, 6))
    d.text((60, H - 70), "geopolcoins.xyz", font=PIX(52), fill=(255, 181, 71))
    note = "Facts, not signals. Entertainment only. NFA."
    d.text((W - 60 - d.textlength(note, font=SANS(24)), H - 58), note, font=SANS(24), fill=(143, 133, 163))
    sprite = os.path.join(ROOT, "meme", "pxmint.png")
    if os.path.exists(sprite):
        from PIL import Image as I
        sp = I.open(sprite).convert("RGBA"); sp = sp.resize((sp.width * 9, sp.height * 9), I.NEAREST)
        im.paste(sp, (W - sp.width - 70, 60), sp)
    return im, d, PIX, SANS


def img_report(s, out):
    im, d, PIX, SANS = canvas("RED FLAG REPORT", (255, 107, 107))
    d.text((60, 190), f"{s['pools']} trending Solana pools checked this week", font=SANS(38), fill=(243, 236, 217))
    d.text((60, 250), f"{s['any']}%", font=PIX(230), fill=(255, 107, 107))
    d.text((60 + d.textlength(f"{s['any']}%", font=PIX(230)) + 30, 330), "had a serious\nred flag", font=PIX(80), fill=(243, 236, 217), spacing=6)
    rows = [("Thin liquidity (under $10k)", s["thin"]), ("Buys but zero sells", s["nosell"]), ("Volume over 50x liquidity", s["vol"]), ("Price +300% in 24h", s["pump"])]
    y = 520
    for label, v in rows:
        d.text((60, y), label, font=SANS(30), fill=(179, 169, 196))
        d.rounded_rectangle((640, y + 4, 640 + 700, y + 34), 8, fill=(37, 28, 56))
        d.rounded_rectangle((640, y + 4, 640 + max(8, int(700 * v / 100)), y + 34), 8, fill=(255, 181, 71))
        d.text((1360, y), f"{v}%", font=SANS(30), fill=(243, 236, 217))
        y += 62
    im.save(out, optimize=True)


def img_war(rows, wk, out):
    im, d, PIX, SANS = canvas("LANGUAGE WAR", (95, 211, 198))
    if not rows:
        d.text((60, 260), "No team on the board yet.", font=PIX(96), fill=(243, 236, 217))
        d.text((60, 390), "Play MAIGA Raid, pick your language team\nand be the first to score.", font=SANS(40), fill=(179, 169, 196), spacing=10)
    else:
        w = rows[0]
        d.text((60, 190), f"Week {wk.split('W')[1]} winner", font=SANS(38), fill=(179, 169, 196))
        d.text((60, 240), TEAM_EN[w["team"]].upper(), font=PIX(170), fill=(255, 181, 71))
        d.text((60, 410), f"{int(w['points']):,} points · {int(w['players'])} players".replace(",", " "), font=SANS(40), fill=(243, 236, 217))
        y = 500; mx = max(int(r["points"]) for r in rows) or 1
        for i, r in enumerate(rows[:5], 1):
            name = TEAM_EN[r["team"]]
            d.text((60, y), f"{i}. {name}", font=SANS(32), fill=(243, 236, 217))
            d.rounded_rectangle((520, y + 6, 520 + max(8, int(760 * int(r["points"]) / mx)), y + 36), 8, fill=(95, 211, 198) if i > 1 else (255, 181, 71))
            d.text((1300, y), f"{int(r['points'])}", font=SANS(32), fill=(179, 169, 196))
            y += 58
    im.save(out, optimize=True)


def img_tip(t, out):
    import textwrap
    im, d, PIX, SANS = canvas("TIP OF THE WEEK", (200, 168, 255))
    y = 200
    for line in textwrap.wrap(t["title"], 34)[:3]:
        d.text((60, y), line, font=PIX(88), fill=(243, 236, 217)); y += 92
    y += 20
    for line in textwrap.wrap(t["quick"], 62)[:6]:
        d.text((60, y), line, font=SANS(32), fill=(179, 169, 196)); y += 46
    im.save(out, optimize=True)


# ---------- report.html
def report_page(s, history):
    e = html.escape
    rows = "".join(f"<tr><td>{e(h['week'])}</td><td>{h['pools']}</td><td><b>{h['any']}%</b></td><td>{h['thin']}%</td><td>{h['nosell']}%</td><td>{h['pump']}%</td></tr>" for h in reversed(history[-26:]))
    bars = "".join(f'<div class="bar"><span>{e(lbl)}</span><i style="--w:{v}%"></i><b>{v}%</b></div>' for lbl, v in
                   [("Thin liquidity (under $10,000)", s["thin"]), ("Buys but zero sells (honeypot sign)", s["nosell"]), ("Volume over 50x the liquidity", s["vol"]), ("Price +300% in 24 hours", s["pump"]), ("Price -60% in 24 hours", s["crash"])])
    updated = dt.date.today().isoformat()
    faq = [("What is the Solana Red Flag Report?", "A free weekly count of public red flags across the trending Solana pools on GeckoTerminal. We sample the trending list four times a day and count each pool once per week."),
           ("Which red flags do you count?", "Thin liquidity under $10,000, many buys with zero sells (a honeypot sign), 24-hour volume over 50 times the liquidity (possible bot volume), and price moves of +300% or -60% in 24 hours. A serious red flag means thin liquidity or buys without sells."),
           ("Does a pool without flags mean it is safe?", "No. These are a few public checks only. Many risks do not show in public data. This is education, not financial advice.")]
    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}, ensure_ascii=False)
    ds_ld = json.dumps({"@context": "https://schema.org", "@type": "Dataset", "name": "Solana Red Flag Report", "description": "Weekly share of trending Solana pools with public red flags (thin liquidity, buys without sells, bot-like volume, extreme price moves).",
                        "url": "https://geopolcoins.xyz/report.html", "license": "https://creativecommons.org/licenses/by/4.0/", "creator": {"@type": "Organization", "name": "geopolcoins.xyz"},
                        "temporalCoverage": f"{history[0]['week'] if history else s['week']}/{s['week']}", "dateModified": updated, "isAccessibleForFree": True}, ensure_ascii=False)
    this_week = (f"<div class=\"big\"><b>{s['any']}%</b><span>of the {s['pools']} trending Solana pools we checked this week had a serious red flag (thin liquidity or buys without any sells).</span></div>"
                 f"<h2>This week</h2>{bars}")
    first = "<div class=\"big\"><span>The snapshots have started. The first weekly numbers appear here on Sunday evening.</span></div>"
    faq_html = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq)
    return f"""<!doctype html>
<html lang="en" data-page="report">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://zslzbfbqrtfpvgbjhssd.supabase.co; manifest-src 'self'; worker-src 'self'; base-uri 'none'; form-action 'self'">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Solana Red Flag Report: weekly scam signals | MAIGA</title>
<meta name="description" content="Each week we count public red flags across trending Solana pools: thin liquidity, honeypot signs, bot volume and wild price moves. Free data, no signals.">
<link rel="canonical" href="https://geopolcoins.xyz/report.html">
<meta property="og:type" content="article"><meta property="og:title" content="Solana Red Flag Report: {s['any']}% of trending pools had a serious red flag">
<meta property="og:description" content="Weekly public red-flag count across trending Solana pools. Facts, not signals.">
<meta property="og:url" content="https://geopolcoins.xyz/report.html"><meta property="og:image" content="https://geopolcoins.xyz/social/report.png"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#120f1e">
<script type="application/ld+json">{ds_ld}</script>
<script type="application/ld+json">{faq_ld}</script>
<style>
@font-face{{font-family:"Jersey 10";src:url(/fonts/jersey-10.woff2) format("woff2");font-display:swap}}
:root{{--night:#120f1e;--cab:#251c38;--line:rgba(241,235,224,.12);--text:#f1ebe0;--dim:#b3a9c4;--mute:#8f85a3;--amber:#ffb547;--red:#ff6b6b;--teal:#5fd3c6;--pix:"Jersey 10",ui-monospace,monospace}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--night);color:var(--text);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
a{{color:var(--amber)}}a:focus-visible,summary:focus-visible{{outline:3px solid var(--teal);outline-offset:2px}}
.skip{{position:absolute;left:8px;top:-60px;background:var(--amber);color:#1a1206;padding:10px 14px;border-radius:8px;font-weight:800}}.skip:focus{{top:8px}}
.wrap{{max-width:980px;margin:0 auto;padding:0 16px}}.top{{display:flex;align-items:center;gap:12px;padding:14px 0;flex-wrap:wrap}}
.brand{{color:var(--text);text-decoration:none;font-weight:800;margin-right:auto}}.brand b{{color:var(--amber)}}.top nav a{{color:var(--dim);text-decoration:none;margin-left:12px}}
h1{{font:400 clamp(44px,7vw,72px)/.95 var(--pix);margin:22px 0 10px}}h1 span{{color:var(--red)}}h2{{font:400 clamp(30px,4vw,40px)/1 var(--pix);margin:36px 0 10px}}
.lead{{color:var(--dim);font-size:18px;max-width:62ch}}
.big{{display:flex;align-items:baseline;gap:18px;flex-wrap:wrap;background:var(--cab);border-radius:16px;padding:18px 20px;margin:18px 0}}
.big b{{font:400 clamp(80px,14vw,140px)/1 var(--pix);color:var(--red)}}.big span{{font-size:20px;max-width:30ch}}
.bar{{display:grid;grid-template-columns:minmax(0,1fr) 2fr 54px;gap:12px;align-items:center;margin:8px 0}}.bar span{{color:var(--dim)}}
.bar i{{display:block;height:16px;border-radius:8px;background:linear-gradient(90deg,var(--amber) var(--w),#2f2446 var(--w))}}.bar b{{text-align:right}}
table{{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}}th,td{{padding:8px 6px;border-bottom:1px solid var(--line);text-align:left}}th{{color:var(--mute);font-weight:600}}
.tw{{overflow-x:auto}}.note{{border:1px dashed rgba(255,181,71,.55);border-radius:12px;padding:10px 14px;background:rgba(255,181,71,.07);font-size:14px}}
.faq{{display:grid;gap:8px}}.faq details{{background:var(--cab);border-radius:12px;padding:12px 14px}}.faq summary{{cursor:pointer;font-weight:700}}.faq p{{margin:8px 0 2px;color:var(--dim)}}
.cta{{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0}}.btn{{display:inline-flex;align-items:center;min-height:44px;padding:0 16px;border-radius:12px;background:var(--amber);color:#1a1206;font-weight:800;text-decoration:none}}.btn.g{{background:var(--cab);color:var(--text);border:1px solid var(--line)}}
footer{{border-top:1px solid var(--line);margin:40px 0 0;padding:18px 0 40px;color:var(--mute);font-size:13.5px;display:flex;gap:14px;flex-wrap:wrap}}footer a{{color:var(--dim)}}
@media (max-width:620px){{.bar{{grid-template-columns:1fr 54px}}.bar i{{grid-column:1/3;grid-row:2}}}}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="wrap">
<header class="top"><a class="brand" href="/"><b>$MAIGA</b> · geopolcoins.xyz</a><nav aria-label="Main"><a href="radar.html">Radar</a><a href="hq.html#checkup">Token Checkup</a><a href="blog.html">Blog</a></nav></header>
<main id="main">
<h1>Solana <span>Red Flag</span> Report</h1>
<p class="lead">Every week we count public red flags across the trending Solana pools. Week {e(s['week'])}, updated {updated}. Facts, not signals: we never name or rate a single token here.</p>
{first if not s['pools'] else this_week}
<div class="cta"><a class="btn" href="hq.html#checkup">Check a token yourself</a><a class="btn g" href="radar.html">See live red flags</a><a class="btn g" href="rug.html">Practise: Spot the Rug Pull</a></div>
<p class="note">Trending means many people trade it now, not that it is good or will go up. No flags does not mean safe. Data: GeckoTerminal public API, sampled four times a day; each pool counts once per week. Education only, not financial advice.</p>
<h2>Past weeks</h2>
<div class="tw"><table><thead><tr><th>Week</th><th>Pools</th><th>Serious flag</th><th>Thin liquidity</th><th>No sells</th><th>+300%</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>You may reuse these numbers with a link to this page (CC BY 4.0).</p>
<section class="faq" aria-labelledby="hQ"><h2 id="hQ">Questions</h2>{faq_html}</section>
</main>
<footer><a href="/">Home</a><a href="radar.html">MAIGA Radar</a><a href="widget.html">Widget</a><a href="blog.html">Blog</a><a href="privacy.html">Privacy</a><a href="legal.html">Legal</a><span>Facts, not signals. Not financial advice.</span></footer>
</div>
<script src="/track.js" data-page="report" defer></script>
<script src="/guide.js" defer></script>
</body>
</html>
"""


def weekly(data_dir):
    wk = week_id()
    s = stats_for(data_dir, wk)
    hist_path = os.path.join(ROOT, "data", "redflag-history.json")
    history = json.load(open(hist_path)) if os.path.exists(hist_path) else []
    history = [h for h in history if h["week"] != wk] + ([s] if s["pools"] else [])
    os.makedirs(os.path.dirname(hist_path), exist_ok=True)
    json.dump(history, open(hist_path, "w"), indent=1)
    war = language_war()
    tip = blog_tip(wk)
    out = os.path.join(ROOT, "social"); os.makedirs(out, exist_ok=True)
    img_war(war, wk, os.path.join(out, "war.png"))
    img_report(s, os.path.join(out, "report.png"))
    img_tip(tip, os.path.join(out, "tip.png"))
    if war:
        top = war[0]
        podium = " · ".join(f"{i}. {TEAM_FLAGS[r['team']]} {TEAM_NAMES[r['team']]}" for i, r in enumerate(war[:3], 1))
        war_txt = (f"🏆 Language War, week {wk.split('W')[1]}: {TEAM_FLAGS[top['team']]} {TEAM_NAMES[top['team']]} wins with {int(top['points'])} points!"
                   f"\n\n{podium}\n\nNew round starts now. Pick your team and play free:\nhttps://geopolcoins.xyz/raid.html")
    else:
        war_txt = "🏆 The MAIGA Raid Language War is open and no team has scored yet.\n\nPick your language team, beat Lord Rugpull and put your country on the board. Free, no wallet:\nhttps://geopolcoins.xyz/raid.html"
    rep_txt = (f"🚩 Red Flag Report: we checked {s['pools']} trending Solana pools this week.\n\n{s['any']}% had a serious red flag."
               f"\n{s['thin']}% thin liquidity · {s['nosell']}% buys with zero sells · {s['pump']}% pumped 300%+ in a day"
               "\n\nFacts, not signals. NFA.\nhttps://geopolcoins.xyz/report.html")
    tip_txt = f"💡 {tip['title']}\n\n{tip['quick'][:150].rsplit(' ', 1)[0]}…\n\n{tip['url']}"
    kit = {"week": wk, "made": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"), "posts": [
        {"day": "Monday", "label": "Language War winner", "image": "social/war.png", "text": fit(war_txt)},
        {"day": "Wednesday", "label": "Red Flag Report", "image": "social/report.png", "text": fit(rep_txt)},
        {"day": "Friday", "label": "Tip of the week", "image": "social/tip.png", "text": fit(tip_txt)}]}
    json.dump(kit, open(os.path.join(out, "kit.json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(ROOT, "report.html"), "w", encoding="utf-8").write(report_page(s, history or [s]))
    print(json.dumps({"week": wk, "pools": s["pools"], "any": s["any"], "war": len(war)}, ensure_ascii=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sample", "weekly"])
    ap.add_argument("--data", default=os.path.join(ROOT, ".growth-data"))
    a = ap.parse_args()
    sample(a.data) if a.cmd == "sample" else weekly(a.data)
