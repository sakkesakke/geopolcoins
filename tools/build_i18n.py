#!/usr/bin/env python3
"""Build the extra site languages (beyond EN/NL/FR).

Source: tools/i18n/<lang>.json  ->  {"geo": {...}, "<page>": {...}, ...}
Output:
  i18n/<page>.js   window.MAIGA_I18N = {es:{...}, pt:{...}, ...}  (merged into the page's T)
  geo-guard.js     extra risk-banner strings between the LANGS markers
English source strings per page: tools/i18n/<page>.en.json (for checking coverage).
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'i18n')
ORDER = ['es', 'pt', 'de', 'tr', 'id', 'vi', 'ar']


def main():
    langs = {}
    for f in sorted(glob.glob(os.path.join(SRC, '*.json'))):
        code = os.path.basename(f)[:-5]
        if '.' in code:
            continue
        langs[code] = json.load(open(f, encoding='utf-8'))
    codes = [c for c in ORDER if c in langs]
    pages = sorted({p for c in codes for p in langs[c] if p != 'geo'})
    os.makedirs(os.path.join(ROOT, 'i18n'), exist_ok=True)
    problems = 0
    for p in pages:
        en_file = os.path.join(SRC, p + '.en.json')
        en = json.load(open(en_file, encoding='utf-8')) if os.path.exists(en_file) else {}
        data = {}
        for c in codes:
            if p not in langs[c]:
                continue
            d = langs[c][p]
            extra = [k for k in d if en and k not in en and not isinstance(d[k], dict) and k not in ('ld', 'ck', 'chart', 'err', 'upd', 'tot')]
            if extra:
                print(f'note {c}/{p}: keys not on page: {extra}')
            data[c] = d
        js = ('/* built by tools/build_i18n.py: do not edit */\n'
              'window.MAIGA_I18N=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
        open(os.path.join(ROOT, 'i18n', p + '.js'), 'w', encoding='utf-8').write(js)
        print(f'i18n/{p}.js  {", ".join(data)}  {len(js)//1024} KB')
    # geo-guard banner strings
    gpath = os.path.join(ROOT, 'geo-guard.js')
    g = open(gpath, encoding='utf-8').read()
    body = ''.join(f'  T.{c} = {json.dumps(langs[c]["geo"], ensure_ascii=False)};\n' for c in codes if 'geo' in langs[c])
    new, n = re.subn(r'(/\*LANGS-START[^\n]*\*/\n).*?(  /\*LANGS-END\*/)', lambda m: m.group(1) + body + m.group(2), g, flags=re.S)
    if n != 1:
        print('geo-guard.js markers missing'); problems += 1
    else:
        open(gpath, 'w', encoding='utf-8').write(new)
    return problems


if __name__ == '__main__':
    sys.exit(main())
