#!/usr/bin/env python3
"""Build the Mindveto adult-content block list (family filter) from MIT-licensed public lists.

Usage: python3 tools/build_ho_adult.py <sinfonietta pornography-hosts> <StevenBlack extensions/porn/clefspeare13/hosts> <bigdargon hostsVN adult hosts-VN>
  git clone --depth 1 https://github.com/Sinfonietta/hostfiles          -> pornography-hosts
  git clone --depth 1 https://github.com/StevenBlack/hosts              -> extensions/porn/clefspeare13/hosts
  curl -L https://raw.githubusercontent.com/bigdargon/hostsVN/master/extensions/adult/hosts-VN
Writes human-override/adult/adult.txt (one registrable host per line) and NOTICE.txt (the MIT notices we must keep).
Run tools/build_ho_lists.py afterwards: it turns adult.txt into the extension ruleset, the Android asset and the network files.
"""
import os, re, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'human-override', 'adult')
DOM = re.compile(r'^(?=.{3,253}$)([a-z0-9-]{1,63}\.)+[a-z]{2,24}$')
# Mainstream sites that must never be blocked by the family filter, even if a source list lists them
NEVER = {'google.com', 'youtube.com', 'bing.com', 'duckduckgo.com', 'yahoo.com', 'wikipedia.org', 'reddit.com', 'x.com', 'twitter.com',
         'facebook.com', 'instagram.com', 'tiktok.com', 'snapchat.com', 'whatsapp.com', 'telegram.org', 't.me', 'discord.com', 'discord.gg',
         'tumblr.com', 'imgur.com', 'pinterest.com', 'patreon.com', 'twitch.tv', 'vimeo.com', 'dailymotion.com', 'archive.org', 'github.com',
         'github.io', 'blogspot.com', 'wordpress.com', 'medium.com', 'substack.com', 'amazonaws.com', 'cloudfront.net', 'akamaized.net',
         'googleusercontent.com', 'fbcdn.net', 'cdninstagram.com', 'apple.com', 'icloud.com', 'microsoft.com', 'live.com', 'outlook.com',
         'office.com', 'linkedin.com', 'netflix.com', 'spotify.com', 'soundcloud.com', 'dropbox.com', 'mega.nz', 'deviantart.com', 'wattpad.com',
         'fandom.com', 'steamcommunity.com', 'steampowered.com', 'mindveto.app', 'geopolcoins.xyz', 'mozilla.org', 'gov.uk', 'europa.eu'}
SOURCES = [('Sinfonietta/hostfiles pornography-hosts', 'MIT', '(c) 2016 Sinfonietta'),
           ('StevenBlack/hosts extensions/porn/clefspeare13', 'MIT', '(c) Steven Black'),
           ('bigdargon/hostsVN extensions/adult', 'MIT', '(c) BigDargon')]


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


if len(sys.argv) != 4: sys.exit(__doc__)
doms = set()
for p in sys.argv[1:]: doms |= read(p)
os.makedirs(OUT, exist_ok=True)
today = datetime.date.today().isoformat()
open(os.path.join(OUT, 'adult.txt'), 'w').write(
    f'# Mindveto family filter: adult content (https://mindveto.app/)\n# Updated: {today}  Domains: {len(doms)}\n'
    '# Built from MIT-licensed public lists, see NOTICE.txt. Sub-domains are blocked too.\n' + '\n'.join(sorted(doms)) + '\n')
mit = ('Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files '
       '(the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, '
       'publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, '
       'subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or '
       'substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING '
       'BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS '
       'OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING '
       'FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.')
open(os.path.join(OUT, 'NOTICE.txt'), 'w').write(
    'Mindveto family filter (adult content list) - third-party notices\n\nThe adult-content domain list is built from these lists:\n\n' +
    ''.join(f'- {n}: {lic} License, {c}\n' for n, lic, c in SOURCES) + '\n' + mit + '\n')
print('adult domains', len(doms))
