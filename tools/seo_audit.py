"""SEO audit for geopolcoins.xyz (the 20 basic checks). Run: python3 tools/seo_audit.py
Prints one line per problem. Exit code 1 if anything important is wrong."""
import glob, html.parser, os, re, sys, json
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://geopolcoins.xyz'
# pages that should NOT be in search on purpose
PRIVATE = {'admin.html', 'reset.html', 'start.html', 'offline.html', '404.html', 'google9970ace9218804f6.html', 'marketing.html'}


class P(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.tags = []; self.heads = []; self.imgs = []; self.links = []; self.meta = {}; self.title = None; self._t = False
        self.canon = None; self.ld = 0; self._ld = False; self.ldtxt = ''; self.lang = None; self.viewport = False

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == 'html': self.lang = a.get('lang')
        if tag == 'title': self._t = True; self.title = ''
        if re.fullmatch(r'h[1-6]', tag): self.heads.append(int(tag[1]))
        if tag == 'img': self.imgs.append(a)
        if tag == 'a' and a.get('href'): self.links.append(a['href'])
        if tag == 'link' and a.get('rel') == 'canonical': self.canon = a.get('href')
        if tag == 'meta':
            k = a.get('name') or a.get('property')
            if k: self.meta[k.lower()] = a.get('content', '')
            if a.get('name') == 'viewport': self.viewport = True
        if tag == 'script' and a.get('type') == 'application/ld+json': self.ld += 1; self._ld = True

    def handle_endtag(self, tag):
        if tag == 'title': self._t = False
        if tag == 'script': self._ld = False

    def handle_data(self, d):
        if self._t: self.title += d
        if self._ld: self.ldtxt += d


def main():
    os.chdir(ROOT)
    pages = sorted(glob.glob('*.html'))
    sitemap = open('sitemap.xml').read()
    in_map = set(re.findall(r'<loc>https://geopolcoins\.xyz/([^<]*)</loc>', sitemap))
    in_map = {('index.html' if u in ('', '/') else u) for u in in_map}
    problems = []
    titles = {}; descs = {}
    for f in pages:
        if f.startswith('google') and f.endswith('.html'): continue
        s = open(f, encoding='utf-8').read(); p = P(); p.feed(s)
        noindex = 'noindex' in p.meta.get('robots', '').lower()
        private = f in PRIVATE or noindex
        def bad(msg): problems.append(f'{f}: {msg}')
        if not p.viewport: bad('no viewport meta (mobile)')
        if f in ('google9970ace9218804f6.html',): continue
        if not p.lang: bad('no <html lang>')
        if private:
            if f in in_map: bad('private/noindex page is in sitemap.xml')
            continue
        if f not in in_map: bad('missing from sitemap.xml')
        if noindex: bad('has noindex')
        t = (p.title or '').strip()
        if not t: bad('no <title>')
        elif len(t) > 65: bad(f'title too long ({len(t)}): {t}')
        elif len(t) < 15: bad(f'title too short: {t}')
        titles.setdefault(t, []).append(f)
        d = p.meta.get('description', '').strip()
        if not d: bad('no meta description')
        elif len(d) > 165: bad(f'description too long ({len(d)})')
        elif len(d) < 50: bad(f'description too short ({len(d)})')
        descs.setdefault(d, []).append(f)
        want = SITE + '/' + ('' if f == 'index.html' else f)
        if not p.canon: bad('no canonical')
        elif p.canon.rstrip('/') != want.rstrip('/'): bad(f'canonical {p.canon} != {want}')
        h1 = p.heads.count(1)
        if h1 != 1: bad(f'{h1} <h1> tags (want 1)')
        for a, b in zip(p.heads, p.heads[1:]):
            if b > a + 1: bad(f'heading jumps h{a} -> h{b}'); break
        for im in p.imgs:
            if 'alt' not in im: bad(f'img without alt: {im.get("src", "")[:60]}')
        if not p.meta.get('og:image'): bad('no og:image')
        if not p.meta.get('og:title'): bad('no og:title')
        if not p.meta.get('twitter:card'): bad('no twitter:card')
        if p.ld == 0: bad('no JSON-LD schema')
        else:
            try:
                for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S): json.loads(blk)
            except Exception as e: bad(f'JSON-LD does not parse: {e}')
        internal = [l for l in p.links if not l.startswith(('http', 'mailto:', 'tel:', '#', 'javascript:'))]
        if len(set(internal)) < 3: bad(f'only {len(set(internal))} internal links')
        for l in p.links:
            if l.startswith('http://') and 'localhost' not in l: bad(f'http link (not https): {l}')
        for l in set(internal):
            path = urlparse(l).path.lstrip('/') or 'index.html'
            if path.endswith('/'): path += 'index.html'
            if not os.path.exists(path) and not os.path.exists(path + '.html'): bad(f'broken internal link: {l}')
        if not re.fullmatch(r'[a-z0-9-]+\.html', f): bad('URL slug has odd characters')
        size = len(s.encode())
        if size > 300_000: bad(f'page is big ({size // 1024} KB)')
    for t, fs in titles.items():
        if len(fs) > 1: problems.append(f'duplicate title on {", ".join(fs)}')
    for d, fs in descs.items():
        if d and len(fs) > 1: problems.append(f'duplicate description on {", ".join(fs)}')
    for u in in_map:
        if not os.path.exists(u): problems.append(f'sitemap lists missing file: {u}')
    # images
    for img in glob.glob('**/*.png', recursive=True) + glob.glob('**/*.jpg', recursive=True) + glob.glob('**/*.webp', recursive=True):
        if 'node_modules' in img: continue
        kb = os.path.getsize(img) // 1024
        if kb > 250: problems.append(f'{img}: image is {kb} KB (compress)')
    for need in ('robots.txt', 'sitemap.xml', 'llms.txt', 'CNAME'):
        if not os.path.exists(need): problems.append(f'missing {need}')
    if 'Sitemap:' not in open('robots.txt').read(): problems.append('robots.txt has no Sitemap line')
    print('\n'.join(problems) if problems else 'all checks passed')
    print(f'-- {len(pages)} pages, {len(in_map)} in sitemap, {len(problems)} problems')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
