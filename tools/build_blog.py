#!/usr/bin/env python3
"""Build the blog: blog.html (index), blog-<slug>.html (articles) and blog-feed.xml (RSS).
Content lives in tools/blog_posts.py. Safe to run again; output is deterministic.
Pages live in the site root on purpose, so the SEO/security audits and IndexNow pick them up."""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blog_posts import POSTS
from blog_posts_nl import POSTS as POSTS_NL
from blog_posts_fr import POSTS as POSTS_FR
from blog_posts_es import POSTS as POSTS_ES
from blog_posts_pt import POSTS as POSTS_PT
from blog_posts_de import POSTS as POSTS_DE
from blog_posts_tr import POSTS as POSTS_TR
from blog_posts_id import POSTS as POSTS_ID
LANGS = {"en": POSTS, "nl": POSTS_NL, "fr": POSTS_FR, "es": POSTS_ES, "pt": POSTS_PT, "de": POSTS_DE, "tr": POSTS_TR, "id": POSTS_ID}
EN_BY_SLUG = {p["slug"]: p for p in POSTS}
for _l in ("nl", "fr", "es", "pt", "de", "tr", "id"):
    for _p in LANGS[_l]:
        _e = EN_BY_SLUG[_p["en"]]
        _p.setdefault("date", _e["date"]); _p.setdefault("tool", _e["tool"])
for _p in POSTS: _p["en"] = _p["slug"]
UI = {
 "en": dict(skip="Skip to content", home="Home", blog="Blog", quick="Quick answer", read="min read", tool="Tool", next="Read next", qs="Questions",
            idx_title="Blog: crypto safety, AI and free tools explained", idx_desc="Plain guides on spotting Solana scams, reading charts, AI and crypto, blockchains, free AI bots for small business, and the $MAIGA meme coin.",
            idx_h="The <span style=\"color:var(--amber)\">blog</span>", idx_lead="Short, honest guides: how to spot scams, read a chart, test AI claims and use our free tools. No hype, no price talk.",
            foot="Education and entertainment. Not financial advice.", privacy="Privacy", legal="Legal", other="Also in",
            months=["January","February","March","April","May","June","July","August","September","October","November","December"]),
 "nl": dict(skip="Naar de inhoud", home="Home", blog="Blog", quick="Kort antwoord", read="min lezen", tool="Tool", next="Lees ook", qs="Vragen",
            idx_title="Blog: cryptoveiligheid, AI en gratis tools uitgelegd", idx_desc="Eenvoudige gidsen over Solana-scams herkennen, grafieken lezen, AI en crypto, blockchains, gratis AI-bots voor kleine zaken en de memecoin $MAIGA.",
            idx_h="De <span style=\"color:var(--amber)\">blog</span>", idx_lead="Korte, eerlijke gidsen: scams herkennen, een grafiek lezen, AI-claims testen en onze gratis tools gebruiken. Geen hype, geen koerspraat.",
            foot="Uitleg en ontspanning. Geen financieel advies.", privacy="Privacy", legal="Juridisch", other="Ook in",
            months=["januari","februari","maart","april","mei","juni","juli","augustus","september","oktober","november","december"]),
 "fr": dict(skip="Aller au contenu", home="Accueil", blog="Blog", quick="Réponse rapide", read="min de lecture", tool="Outil", next="À lire aussi", qs="Questions",
            idx_title="Blog : sécurité crypto, IA et outils gratuits expliqués", idx_desc="Des guides simples pour repérer les arnaques Solana, lire un graphique, comprendre l'IA et la crypto, les blockchains, les bots IA gratuits et le mème coin $MAIGA.",
            idx_h="Le <span style=\"color:var(--amber)\">blog</span>", idx_lead="Des guides courts et honnêtes : repérer les arnaques, lire un graphique, tester les promesses de l'IA et utiliser nos outils gratuits. Sans hype, sans parler de prix.",
            foot="Éducation et divertissement. Pas un conseil financier.", privacy="Confidentialité", legal="Mentions légales", other="Aussi en",
            months=["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"]),
 "es": dict(skip="Saltar al contenido", home="Inicio", blog="Blog", quick="Respuesta rápida", read="min de lectura", tool="Herramienta", next="Lee también", qs="Preguntas",
            idx_title="Blog: seguridad cripto, IA y herramientas gratis", idx_desc="Guías sencillas para detectar estafas en Solana, leer gráficos, entender la IA y la cripto, las blockchains, bots de IA gratis y la meme coin $MAIGA.",
            idx_h="El <span style=\"color:var(--amber)\">blog</span>", idx_lead="Guías cortas y honestas: detectar estafas, leer un gráfico, poner a prueba las promesas de la IA y usar nuestras herramientas gratis. Sin hype, sin hablar de precios.",
            foot="Educación y entretenimiento. No es asesoramiento financiero.", privacy="Privacidad", legal="Aviso legal", other="También en",
            months=["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]),
 "pt": dict(skip="Pular para o conteúdo", home="Início", blog="Blog", quick="Resposta rápida", read="min de leitura", tool="Ferramenta", next="Leia também", qs="Perguntas",
            idx_title="Blog: segurança cripto, IA e ferramentas grátis", idx_desc="Guias simples para identificar golpes na Solana, ler gráficos, entender IA e cripto, blockchains, bots de IA grátis e a meme coin $MAIGA.",
            idx_h="O <span style=\"color:var(--amber)\">blog</span>", idx_lead="Guias curtos e honestos: identificar golpes, ler um gráfico, testar promessas de IA e usar nossas ferramentas grátis. Sem hype, sem papo de preço.",
            foot="Educação e entretenimento. Não é aconselhamento financeiro.", privacy="Privacidade", legal="Aviso legal", other="Também em",
            months=["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"]),
 "de": dict(skip="Zum Inhalt springen", home="Start", blog="Blog", quick="Kurze Antwort", read="Min. Lesezeit", tool="Tool", next="Weiterlesen", qs="Fragen",
            idx_title="Blog: Krypto-Sicherheit, KI und kostenlose Tools", idx_desc="Einfache Guides zum Erkennen von Solana-Betrug, Charts lesen, KI und Krypto, Blockchains, kostenlose KI-Bots und den Meme-Coin $MAIGA.",
            idx_h="Der <span style=\"color:var(--amber)\">Blog</span>", idx_lead="Kurze, ehrliche Guides: Betrug erkennen, Charts lesen, KI-Versprechen testen und unsere kostenlosen Tools nutzen. Kein Hype, kein Kursgerede.",
            foot="Bildung und Unterhaltung. Keine Finanzberatung.", privacy="Datenschutz", legal="Rechtliches", other="Auch auf",
            months=["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]),
 "tr": dict(skip="İçeriğe geç", home="Ana sayfa", blog="Blog", quick="Kısa cevap", read="dk okuma", tool="Araç", next="Şunu da oku", qs="Sorular",
            idx_title="Blog: kripto güvenliği, yapay zekâ ve ücretsiz araçlar", idx_desc="Solana dolandırıcılıklarını fark etme, grafik okuma, yapay zekâ ve kripto, blockchain, ücretsiz yapay zekâ botları ve $MAIGA üzerine sade rehberler.",
            idx_h="<span style=\"color:var(--amber)\">Blog</span>", idx_lead="Kısa ve dürüst rehberler: dolandırıcılığı fark et, grafik oku, yapay zekâ vaatlerini test et ve ücretsiz araçlarımızı kullan. Abartı yok, fiyat konuşması yok.",
            foot="Eğitim ve eğlence. Yatırım tavsiyesi değildir.", privacy="Gizlilik", legal="Yasal", other="Diğer diller",
            months=["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]),
 "id": dict(skip="Langsung ke konten", home="Beranda", blog="Blog", quick="Jawaban singkat", read="menit baca", tool="Alat", next="Baca juga", qs="Pertanyaan",
            idx_title="Blog: keamanan kripto, AI, dan alat gratis", idx_desc="Panduan sederhana untuk mengenali penipuan Solana, membaca grafik, memahami AI dan kripto, blockchain, bot AI gratis, dan meme coin $MAIGA.",
            idx_h="<span style=\"color:var(--amber)\">Blog</span>", idx_lead="Panduan singkat dan jujur: kenali penipuan, baca grafik, uji janji AI, dan pakai alat gratis kami. Tanpa hype, tanpa obrolan harga.",
            foot="Edukasi dan hiburan. Bukan nasihat keuangan.", privacy="Privasi", legal="Hukum", other="Juga dalam",
            months=["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]),
}
LNAME = {"en": "English", "nl": "Nederlands", "fr": "Français", "es": "Español", "pt": "Português", "de": "Deutsch", "tr": "Türkçe", "id": "Bahasa Indonesia"}
def fname(lang, slug=None):
    if slug is None: return "blog.html" if lang == "en" else f"blog-{lang}.html"
    return f"blog-{slug}.html" if lang == "en" else f"blog-{lang}-{slug}.html"
def alt(lang, en_slug):
    if en_slug is None: return fname(lang)
    p = next((q for q in LANGS[lang] if q["en"] == en_slug), None)   # a post may exist in fewer languages
    return fname(lang, p["slug"]) if p else None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://geopolcoins.xyz/"
CSP = ("default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
       "font-src 'self'; connect-src 'self' https://zslzbfbqrtfpvgbjhssd.supabase.co; manifest-src 'self'; worker-src 'self'; frame-src 'none'; base-uri 'none'; form-action 'self'")
TAGC = {"Safety": "#ff6b6b", "Veiligheid": "#ff6b6b", "Sécurité": "#ff6b6b", "AI": "#c8a8ff", "IA": "#c8a8ff", "Learn": "#5fd3c6", "Leren": "#5fd3c6", "Apprendre": "#5fd3c6", "Business": "#ffb547", "Create": "#f3ecd9", "Maken": "#f3ecd9", "Créer": "#f3ecd9", "$MAIGA": "#ffb547"}
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

def block(b, lang="en"):
    k, v = b
    if k == "p": return f"<p>{inline(v)}</p>"
    if k == "h2": return f"<h2>{inline(v)}</h2>"
    if k in ("ul", "ol"): return f"<{k}>" + "".join(f"<li>{inline(i)}</li>" for i in v) + f"</{k}>"
    if k == "quick": return f'<div class="quick"><b>{UI[lang]["quick"]}</b><p>{inline(v)}</p></div>'
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
.langs{font-size:14px;color:var(--mute);margin:-12px 0 22px}.langs a{color:var(--dim);margin-right:10px}
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

def head(title, desc, url, ld, ogtype="article", lang="en", alts=None):
    lds = "".join(f'<script type="application/ld+json"{(" id=" + chr(34) + "ld-crumbs" + chr(34)) if d.get("@type") == "BreadcrumbList" else ""}>{json.dumps(d, ensure_ascii=False, separators=(",", ":"))}</script>\n' for d in ld)
    t, d = html.escape(title), html.escape(desc)
    hl = "".join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{f}">\n' for l, f in (alts or {}).items()) + (f'<link rel="alternate" hreflang="x-default" href="{SITE}{alts["en"]}">\n' if alts else "")
    u = UI[lang]
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
{hl}<link rel="alternate" type="application/rss+xml" title="geopolcoins.xyz blog" href="/blog-feed.xml">
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
<a class="skip" href="#main">{u["skip"]}</a>
<header class="top"><a class="brand" href="/"><b>$MAIGA</b> · geopolcoins.xyz</a><nav aria-label="Main"><a href="/{fname(lang)}">{u["blog"]}</a><a href="/radar.html">Radar</a><a href="/hq.html#checkup">Token Checkup</a><a href="/kronos.html">Kronos Lab</a></nav></header>
"""

def foot(lang):
    u = UI[lang]
    return f"""<footer><a href="/">{u["home"]}</a><a href="/{fname(lang)}">{u["blog"]}</a><a href="/blog-feed.xml">RSS</a><a href="https://www.youtube.com/@geopolcoins" target="_blank" rel="noopener noreferrer">YouTube</a><a href="/privacy.html">{u["privacy"]}</a><a href="/legal.html">{u["legal"]}</a><span>{u["foot"]}</span></footer>
<script src="/track.js" data-page="blog" defer></script>
<script src="/guide.js" defer></script>
</body>
</html>
"""

def date_h(d, lang="en"):
    import datetime
    x = datetime.date.fromisoformat(d)
    return f"{x.day} {UI[lang]['months'][x.month-1]} {x.year}"

def card(p, h="h3", lang="en"):
    c = TAGC.get(p["tag"], "#ffb547")
    return (f'<a class="card" href="/{fname(lang, p["slug"])}"><span class="tag" style="background:{c}">{html.escape(p["tag"])}</span>'
            f'<{h}>{html.escape(p["title"])}</{h}><p>{html.escape(p["desc"])}</p></a>')

def article(p, i, lang="en"):
    u = UI[lang]; posts = LANGS[lang]
    url = SITE + fname(lang, p["slug"])
    alts = {l: a for l in LANGS if (a := alt(l, p["en"]))}
    words = sum(len(plain(v if isinstance(v, str) else " ".join(v) if isinstance(v, list) else " ".join(v)).split()) for k, v in p["body"])
    ld = [{"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["desc"], "datePublished": p["date"],
           "dateModified": p.get("updated", p["date"]), "author": ORG, "publisher": ORG, "mainEntityOfPage": url, "image": SITE + "og-image.jpg",
           "inLanguage": lang, "wordCount": words, "about": p["tool"][0], "isAccessibleForFree": True},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": u["home"], "item": SITE},
              {"@type": "ListItem", "position": 2, "name": u["blog"], "item": SITE + fname(lang)},
              {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]}]
    if p.get("faq"):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]})
    c = TAGC.get(p["tag"], "#ffb547")
    others_l = " ".join(f'<a href="/{alts[l]}" hreflang="{l}" lang="{l}">{LNAME[l]}</a>' for l in alts if l != lang)
    out = [head(p["title"], p["desc"], url, ld, lang=lang, alts=alts), '<main id="main" class="wrap">',
           f'<nav class="crumbs" aria-label="Breadcrumb"><a href="/">{u["home"]}</a> › <a href="/{fname(lang)}">{u["blog"]}</a></nav>',
           f'<article><span class="tag" style="background:{c}">{html.escape(p["tag"])}</span><h1>{html.escape(p["title"])}</h1>',
           f'<p class="meta">{date_h(p["date"], lang)} · {max(1, round(words / 200))} {u["read"]} · {u["tool"]}: <a href="{html.escape(p["tool"][1])}">{html.escape(p["tool"][0])}</a></p>',
           f'<p class="langs">{u["other"]}: {others_l}</p>']
    out += [block(b, lang) for b in p["body"]]
    if p.get("faq"):
        out.append(f'<h2>{u["qs"]}</h2><div class="faq">' + "".join(
            f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in p["faq"]) + "</div>")
    out.append("</article>")
    others = [q for q in posts if q is not p]
    rel = [q for q in others if q["tag"] == p["tag"]][:2]
    rel += [q for q in others if q not in rel][: 3 - len(rel)]
    out.append(f'<h2>{u["next"]}</h2><ul class="more">' + "".join(f"<li>{card(q, lang=lang)}</li>" for q in rel) + "</ul>")
    out.append("</main>")
    out.append(foot(lang))
    return "\n".join(out)

def index(lang="en"):
    u = UI[lang]; posts = LANGS[lang]
    url = SITE + fname(lang)
    alts = {l: fname(l) for l in LANGS}
    ld = [{"@context": "https://schema.org", "@type": "Blog", "name": "geopolcoins.xyz blog", "url": url, "inLanguage": lang, "publisher": ORG,
           "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": SITE + fname(lang, p["slug"]), "datePublished": p["date"]} for p in posts]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": u["home"], "item": SITE},
              {"@type": "ListItem", "position": 2, "name": u["blog"], "item": url}]}]
    others_l = " ".join(f'<a href="/{alts[l]}" hreflang="{l}" lang="{l}">{LNAME[l]}</a>' for l in LANGS if l != lang)
    out = [head(u["idx_title"], u["idx_desc"], url, ld, "website", lang=lang, alts=alts),
           '<main id="main" class="wrap" style="max-width:1100px">',
           f'<nav class="crumbs" aria-label="Breadcrumb"><a href="/">{u["home"]}</a> › {u["blog"]}</nav>',
           f'<h1>{u["idx_h"]}</h1>',
           f'<p class="lead">{u["idx_lead"]}</p>', f'<p class="langs" style="margin:6px 0 0">{u["other"]}: {others_l}</p>',
           '<ul class="grid">' + "".join(f"<li>{card(p, 'h2', lang)}</li>" for p in posts) + "</ul>", "</main>", foot(lang)]
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

HOME_PICKS = ["solana-token-scam-check", "trending-solana-tokens-red-flags", "can-ai-predict-crypto-prices"]


def main():
    names = []
    for lang, posts in LANGS.items():
        seen = set()
        assert {p["en"] for p in posts} <= set(EN_BY_SLUG), f"{lang}: every post needs an English original"
        for i, p in enumerate(posts):
            assert p["slug"] not in seen and re.fullmatch(r"[a-z0-9-]+", p["slug"]); seen.add(p["slug"])
            assert len(p["desc"]) <= 165, (lang, p["slug"], len(p["desc"]))
            assert len(p["title"]) <= 80, (lang, p["slug"], len(p["title"]))
            f = fname(lang, p["slug"]); names.append(f)
            open(os.path.join(ROOT, f), "w", encoding="utf-8").write(article(p, i, lang))
        open(os.path.join(ROOT, fname(lang)), "w", encoding="utf-8").write(index(lang)); names.append(fname(lang))
    open(os.path.join(ROOT, "blog-feed.xml"), "w", encoding="utf-8").write(feed())
    # three featured guides per language for the homepage "From the blog" block
    picks = {}
    for lang, posts in LANGS.items():
        by_en = {p["en"] if lang != "en" else p["slug"]: p for p in posts}
        picks[lang] = {"all": "/" + fname(lang), "posts": [{"t": by_en[e]["title"], "d": by_en[e]["desc"], "tag": by_en[e]["tag"], "u": "/" + fname(lang, by_en[e]["slug"])} for e in HOME_PICKS]}
    os.makedirs(os.path.join(ROOT, "i18n"), exist_ok=True)
    open(os.path.join(ROOT, "i18n", "blog-picks.js"), "w", encoding="utf-8").write(
        "/* built by tools/build_blog.py: do not edit */\nwindow.MAIGA_BLOG=" + json.dumps(picks, ensure_ascii=False, separators=(",", ":")) + ";\n")
    sm = os.path.join(ROOT, "sitemap.xml"); s = open(sm, encoding="utf-8").read()
    add = ""
    for name in names:
        if f"{SITE}{name}</loc>" not in s:
            add += f"  <url><loc>{SITE}{name}</loc><lastmod>2026-11-06</lastmod><changefreq>monthly</changefreq><priority>{'0.8' if name in ('blog.html','blog-nl.html','blog-fr.html','blog-es.html','blog-pt.html','blog-de.html','blog-tr.html','blog-id.html') else '0.6'}</priority></url>\n"
    if add:
        s = s.replace("</urlset>", add + "</urlset>"); open(sm, "w", encoding="utf-8").write(s)
    print(f"blog: {len(names)} pages in {len(LANGS)} languages; sitemap +{add.count('<url>')}")

if __name__ == "__main__":
    main()
