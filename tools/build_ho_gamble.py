#!/usr/bin/env python3
"""Build the Mindveto gambling block list (family filter) from an MIT-licensed public list plus our own additions.

Usage: python3 tools/build_ho_gamble.py <Sinfonietta/hostfiles gambling-hosts>
  git clone --depth 1 https://github.com/Sinfonietta/hostfiles   -> gambling-hosts
Reads human-override/gamble/own.txt, writes human-override/gamble/gamble.txt.
Run tools/build_ho_lists.py afterwards (extension ruleset, Android asset, network files).
"""
import os, re, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, '..', 'human-override', 'gamble')
DOM = re.compile(r'^(?=.{3,253}$)([a-z0-9-]{1,63}\.)+[a-z]{2,24}$')
# never block these, even if a source lists them (sport news, app stores, payment, big platforms)
NEVER = {'google.com', 'youtube.com', 'apple.com', 'microsoft.com', 'paypal.com', 'espn.com', 'bbc.co.uk', 'sporza.be', 'nos.nl',
         'lequipe.fr', 'wikipedia.org', 'reddit.com', 'twitch.tv', 'steampowered.com', 'mindveto.app', 'geopolcoins.xyz'}


def read(path):
    out = set()
    for line in open(path, encoding='utf-8', errors='ignore'):
        line = line.split('#')[0].strip().lower()
        if not line: continue
        parts = line.split()
        d = parts[-1] if parts[0] in ('0.0.0.0', '127.0.0.1') else parts[0]
        d = d[4:] if d.startswith('www.') else d
        if DOM.match(d) and d not in NEVER and not any(d.endswith('.' + n) for n in NEVER): out.add(d)
    return out


if len(sys.argv) != 2: sys.exit(__doc__)
doms = read(sys.argv[1]) | read(os.path.join(G, 'own.txt'))
today = datetime.date.today().isoformat()
open(os.path.join(G, 'gamble.txt'), 'w').write(
    f'# Mindveto family filter: gambling (https://mindveto.app/)\n# Updated: {today}  Domains: {len(doms)}\n'
    '# Sinfonietta/hostfiles gambling-hosts (MIT, (c) 2016 Sinfonietta) + own additions. Sub-domains are blocked too.\n'
    + '\n'.join(sorted(doms)) + '\n')
print('gambling domains', len(doms))
