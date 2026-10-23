#!/usr/bin/env python3
"""Build downloads/maiga-factory-offline.zip: the Meme Factory + Meme Studio as plain HTML files
that open from the computer (file://). Run from the repo root after changing factory.html or meme.html:
    python3 tools/build_offline.py
No tracking, no service worker, links point back to geopolcoins.xyz, pictures are inlined so downloads work."""
import base64, json, re, zipfile, io, os

SITE = 'https://geopolcoins.xyz/'
LOCAL = {'factory.html': 'maiga-factory.html', 'meme.html': 'maiga-meme-studio.html'}

def b64(path):
    return 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode()

def common(s):
    s = re.sub(r'<script>\(function\(\)\{try\{if\(navigator\.webdriver.*?</script>\n?', '', s, flags=re.S)  # page counter
    s = re.sub(r'<script src="(pwa|guide)\.js" defer></script>\n?', '', s)
    s = re.sub(r'<link rel="(icon|apple-touch-icon|manifest)"[^>]*>\n?', '', s)
    def link(m):
        url = m.group(1)
        if url.startswith(('http', '#', 'data:', 'mailto:')): return m.group(0)
        page = url.split('#')[0]
        if page in LOCAL: return 'href="' + LOCAL[page] + url[len(page):] + '"'
        return 'href="' + SITE + url.lstrip('/') + '"'
    s = re.sub(r'href="([^"]*)"', link, s)
    s = s.replace("location.href='meme.html#'", "location.href='maiga-meme-studio.html#'")
    return s

f = common(open('factory.html').read())
f = re.sub(r'<section class="card boot" id="boot".*?</section>\n*', '<p class="note" style="text-align:center;margin-top:18px">You are using the offline copy of the MAIGA Meme Factory. Latest version: <a href="https://geopolcoins.xyz/factory.html">geopolcoins.xyz/factory.html</a></p>\n', f, flags=re.S)
f = f.replace('<a href="#boot" class="dlnav">&#11015; DOWNLOAD</a>', '')
assert 'dlnav">' not in f

m = common(open('meme.html').read())
tpl = open('meme/templates.json').read()
m = m.replace("fetch('meme/templates.json').then(function(r){return r.json();})", 'Promise.resolve(window.TPLDATA)')
m = m.replace('<script>\n(function(){', '<script>window.TPLDATA=' + tpl + ';</script>\n<script>\n(function(){', 1)
for png in sorted(os.listdir('meme')):
    if png.endswith('.png'): m = m.replace("'meme/" + png + "'", "'" + b64('meme/' + png) + "'").replace('"meme/' + png + '"', '"' + b64('meme/' + png) + '"')
m = m.replace("'meme/'+p.id+'.png'", "PXD[p.id]").replace("('meme/'+s.k+'.png')", "PXD[s.k]")
pxd = {n[:-4]: b64('meme/' + n) for n in sorted(os.listdir('meme')) if n.endswith('.png')}
pxd['bolt'] = b64('bolt.png'); pxd['logo'] = b64('logo.png')
m = m.replace("src:'bolt.png'", "src:PXD.bolt").replace("src:'logo.png'", "src:PXD.logo")
m = m.replace('<script>window.TPLDATA=', '<script>window.PXD=' + json.dumps(pxd) + ';var PXD=window.PXD;window.TPLDATA=', 1)
assert 'meme/templates.json' not in m and "'meme/" not in m and 'src="meme/' not in m, 'unreplaced local file'

readme = """MAIGA MEME FACTORY - OFFLINE COPY
=================================
EN  Double-click maiga-factory.html. It opens in your browser. Free templates work without internet.
    The community hub, classic meme templates and AI mode need internet. Nothing is installed.
NL  Dubbelklik op maiga-factory.html. Het opent in je browser. Gratis sjablonen werken zonder internet.
    De community hub, klassieke meme-sjablonen en AI hebben internet nodig. Er wordt niets geinstalleerd.
FR  Double-clique sur maiga-factory.html. Il s'ouvre dans ton navigateur. Les modeles gratuits marchent sans internet.
    Le hub, les memes classiques et le mode IA demandent internet. Rien n'est installe.

Your AI key (optional) goes only to the provider you pick. Never share it.
Classic meme templates: memegen by Jace Browning (MIT), served by memegen.link.
Entertainment only. Not financial advice. Nothing is posted or launched for you.
Latest version and terms: https://geopolcoins.xyz/factory.html
"""
buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, data in (('maiga-factory/maiga-factory.html', f), ('maiga-factory/maiga-meme-studio.html', m), ('maiga-factory/README.txt', readme)):
        info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o644 << 16
        z.writestr(info, data)
open('downloads/maiga-factory-offline.zip', 'wb').write(buf.getvalue())
print('downloads/maiga-factory-offline.zip', len(buf.getvalue()) // 1024, 'KB')
