#!/usr/bin/env python3
"""Build the public Human Override block lists from human-override/extension/lists.json.

Writes (in human-override/):
  lists.json      - read by the extension once a day
  domains.txt     - one domain per line (NextDNS, Control D, router lists)
  hosts.txt       - hosts-file format (0.0.0.0 domain), for Windows/Mac/Linux and Pi-hole
  adblock.txt     - AdGuard / AdGuard DNS / AdGuard Home / uBlock Origin syntax (||domain^)
Paths like bing.com/chat cannot be blocked by DNS; they are only blocked by the browser extension.
"""
import json, os, re, shutil, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'human-override')
src = os.path.join(D, 'extension', 'lists.json')
L = json.load(open(src))
DOM = re.compile(r'^([a-z0-9-]{1,63}\.)+[a-z]{2,24}$')
doms = sorted({d for c in L['categories'].values() for d in c['domains'] if DOM.match(d)})
shutil.copyfile(src, os.path.join(D, 'lists.json'))
today = datetime.date.today().isoformat()
head = ['Human Override AI block list (https://geopolcoins.xyz/human-override.html)', f'Updated: {today}  Domains: {len(doms)}',
        'Free to use. Blocks AI chatbots, AI search, AI image/video/voice/music, AI writing/homework and AI coding services.']
open(os.path.join(D, 'domains.txt'), 'w').write('\n'.join('# ' + h for h in head) + '\n' + '\n'.join(doms) + '\n')
open(os.path.join(D, 'hosts.txt'), 'w').write('\n'.join('# ' + h for h in head) + '\n' + '\n'.join(f'0.0.0.0 {d}\n0.0.0.0 www.{d}' for d in doms) + '\n')
open(os.path.join(D, 'adblock.txt'), 'w').write('! Title: Human Override AI block list\n' + '\n'.join('! ' + h for h in head) + '\n' + '\n'.join(f'||{d}^' for d in doms) + '\n')
print('domains', len(doms))
