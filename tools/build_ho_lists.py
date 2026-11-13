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
AI_CATS = {k: c for k, c in L['categories'].items() if k != 'social'}   # social media is an optional extension-only category
doms = sorted({d for c in AI_CATS.values() for d in c['domains'] if DOM.match(d)})
# Google Translate proxy copies (<site-with-dashes>.translate.goog) for DNS-based tools (Android app, hosts, routers)
proxies = sorted({d.replace('-', '--').replace('.', '-') + '.translate.goog' for d in doms})
dns_doms = sorted(set(doms) | {p for p in proxies if DOM.match(p)})
shutil.copyfile(src, os.path.join(D, 'lists.json'))
today = datetime.date.today().isoformat()
head = ['Mindveto AI block list (https://mindveto.app/)', f'Updated: {today}  Domains: {len(doms)}',
        'Free to use. Blocks AI chatbots, AI search, AI image/video/voice/music, AI writing/homework and AI coding services.']
open(os.path.join(D, 'domains.txt'), 'w').write('\n'.join('# ' + h for h in head) + '\n' + '\n'.join(dns_doms) + '\n')
open(os.path.join(D, 'hosts.txt'), 'w').write('\n'.join('# ' + h for h in head) + '\n' + '\n'.join(f'0.0.0.0 {d}\n0.0.0.0 www.{d}' for d in doms) + '\n' + '\n'.join(f'0.0.0.0 {p}' for p in proxies) + '\n')
open(os.path.join(D, 'adblock.txt'), 'w').write('! Title: Mindveto AI block list\n' + '\n'.join('! ' + h for h in head) + '\n' + '\n'.join(f'||{d}^' for d in dns_doms) + '\n')
print('domains', len(doms))

# ---------- Pro pack for IT departments (justice, government, schools, companies) ----------
P = os.path.join(D, 'pro'); os.makedirs(P, exist_ok=True)
paths = sorted({p for c in AI_CATS.values() for p in c.get('paths', [])})
cr = '(c) 2026 Amghar Said. All rights reserved. Mindveto - the AI kill switch (formerly Human Override). https://mindveto.app/'
pats = [f'{d}' for d in doms] + paths
json.dump({"_comment": "Chrome and Edge enterprise policy (GPO/Intune/Jamf/Google Admin). " + cr,
           "URLBlocklist": pats}, open(os.path.join(P, 'chrome-edge-policy.json'), 'w'), indent=1)
json.dump({"_comment": cr, "policies": {"WebsiteFilter": {"Block": [f"*://*.{d}/*" for d in doms] + [f"*://{d}/*" for d in doms] + [f"*://{p}*" for p in paths] + [f"*://*.{p}*" for p in paths]}}},
          open(os.path.join(P, 'firefox-policies.json'), 'w'), indent=1)
open(os.path.join(P, 'rpz.zone'), 'w').write(f'; Mindveto RPZ zone for BIND / PowerDNS / Infoblox / Knot. {cr}\n$TTL 300\n@ IN SOA localhost. root.localhost. ({today.replace("-", "")}01 3600 600 86400 300)\n@ IN NS localhost.\n' +
    ''.join(f'{d} CNAME .\n*.{d} CNAME .\n' for d in doms))
open(os.path.join(P, 'unbound.conf'), 'w').write(f'# Mindveto for Unbound / OPNsense / pfSense. {cr}\nserver:\n' + ''.join(f'  local-zone: "{d}." always_nxdomain\n' for d in doms))
open(os.path.join(P, 'dnsmasq.conf'), 'w').write(f'# Mindveto for dnsmasq / OpenWrt / Pi-hole (custom dnsmasq). {cr}\n' + ''.join(f'address=/{d}/0.0.0.0\n' for d in doms))
open(os.path.join(P, 'squid-acl.conf'), 'w').write(f'# Mindveto for Squid proxy. {cr}\nacl human_override_ai dstdomain ' + ' '.join('.' + d for d in doms) + '\nhttp_access deny human_override_ai\n')
open(os.path.join(P, 'firewall-edl.txt'), 'w').write(''.join(f'{d}\n*.{d}\n' for d in doms))
ps = [f'# Mindveto for Windows Server DNS (run as administrator on the DNS server). {cr}',
      '# Adds DNS query resolution policies that refuse AI domains for all clients.',
      '# Remove with: Get-DnsServerQueryResolutionPolicy | Where-Object Name -like "HumanOverrideAI*" | ForEach-Object { Remove-DnsServerQueryResolutionPolicy -Name $_.Name -Force }',
      'Get-DnsServerQueryResolutionPolicy -ErrorAction SilentlyContinue | Where-Object Name -like "HumanOverrideAI*" | ForEach-Object { Remove-DnsServerQueryResolutionPolicy -Name $_.Name -Force }']
for i in range(0, len(doms), 20):
    part = doms[i:i + 20]
    crit = 'EQ,' + ','.join(f'*.{d},{d}' for d in part)
    ps.append(f"Add-DnsServerQueryResolutionPolicy -Name 'HumanOverrideAI{i // 20 + 1}' -Action DENY -FQDN '{crit}' -ProcessingOrder {i // 20 + 1}")
ps.append('Write-Host "Mindveto: AI domains are now refused by this DNS server."')
open(os.path.join(P, 'windows-dns-server.ps1'), 'w').write('\r\n'.join(ps) + '\r\n')
open(os.path.join(P, 'README.txt'), 'w').write(f'''HUMAN OVERRIDE PRO PACK - the AI kill switch for organisations
{cr}

For IT departments of courts, police, government, schools and companies that must keep AI chatbots and AI tools
off their network and devices. Domains: {len(doms)}. Updated: {today}. Fresh copies: https://geopolcoins.xyz/human-override/pro/

Pick what fits your network (you can combine them):

1. Browser policy on every PC (no extension needed)
   chrome-edge-policy.json  -> Chrome and Edge policy "URLBlocklist" (Group Policy, Intune, Jamf or Google Admin).
   firefox-policies.json    -> put in the Firefox "distribution" folder or push via Group Policy ("WebsiteFilter").

2. DNS server (blocks every device and app on the network)
   rpz.zone                 -> BIND, PowerDNS, Infoblox, Knot (Response Policy Zone).
   windows-dns-server.ps1   -> Windows Server DNS (one query resolution policy).
   unbound.conf             -> Unbound, OPNsense, pfSense.
   dnsmasq.conf             -> dnsmasq, OpenWrt, Pi-hole.

3. Proxy and firewall
   squid-acl.conf           -> Squid proxy.
   firewall-edl.txt         -> External Dynamic List / threat feed for Palo Alto, Fortinet, Check Point, Sophos and others.

Honest limits: DNS and firewall lists block whole domains; AI built into allowed services, AI running offline on a
device, and traffic over a VPN or another DNS (DNS-over-HTTPS) can bypass them. Block outside DNS/DoH and VPNs on your
firewall for full effect. Test in a pilot group first.

Family filter (optional, not AI): adult-content lists in the same formats at https://geopolcoins.xyz/human-override/adult/
(hosts.txt, domains.txt, adblock.txt; MIT-licensed sources, see NOTICE.txt there). SafeSearch on a DNS server:
answer google.com/www.google.<tld> with CNAME forcesafesearch.google.com, www.bing.com with strict.bing.com,
duckduckgo.com with safe.duckduckgo.com and www.youtube.com/m.youtube.com/youtubei.googleapis.com with restrict.youtube.com.
Gambling and dating (optional): https://geopolcoins.xyz/human-override/gamble/ and .../dating/ (same formats).
Anti-bypass (optional): web proxies, VPN services, Tor and secure-DNS (DoH/DoT) addresses at
https://geopolcoins.xyz/human-override/bypass/ (same formats). Also block outgoing port 853 (DoT) and set the browser
policy DnsOverHttpsMode = off (Chrome/Edge) or DNSOverHTTPS Enabled=false (Firefox).

Terms of use (provided "as is", limits of liability): https://mindveto.app/terms/
Help with roll-out: hello@mindveto.app · https://mindveto.app/network/
''')
print('pro pack files', len(os.listdir(P)))

# ---------- family filter: adult content (optional, OFF by default; built by tools/build_ho_adult.py) ----------
A = os.path.join(D, 'adult')
adult = sorted({l.strip() for l in open(os.path.join(A, 'adult.txt')) if l.strip() and not l.startswith('#') and DOM.match(l.strip())})
ahead = ['Mindveto family filter: adult content (https://mindveto.app/)', f'Updated: {today}  Domains: {len(adult)}',
         'Optional list. Built from MIT-licensed public lists, see https://geopolcoins.xyz/human-override/adult/NOTICE.txt']
open(os.path.join(A, 'domains.txt'), 'w').write('\n'.join('# ' + h for h in ahead) + '\n' + '\n'.join(adult) + '\n')
open(os.path.join(A, 'hosts.txt'), 'w').write('\n'.join('# ' + h for h in ahead) + '\n' + '\n'.join(f'0.0.0.0 {d}\n0.0.0.0 www.{d}' for d in adult) + '\n')
open(os.path.join(A, 'adblock.txt'), 'w').write('! Title: Mindveto family filter (adult content)\n' + '\n'.join('! ' + h for h in ahead) + '\n' + '\n'.join(f'||{d}^' for d in adult) + '\n')
# browser extension: one static ruleset, switched on by the extension only when the family filter is on
CH = 10000
arules, rid = [], 1
for i in range(0, len(adult), CH):
    part = adult[i:i + CH]
    arules.append({'id': rid, 'priority': 1, 'action': {'type': 'redirect', 'redirect': {'extensionPath': '/blocked.html?f=adult'}},
                   'condition': {'requestDomains': part, 'resourceTypes': ['main_frame']}}); rid += 1
    arules.append({'id': rid, 'priority': 1, 'action': {'type': 'block'},
                   'condition': {'requestDomains': part, 'resourceTypes': ['sub_frame', 'script', 'xmlhttprequest', 'websocket', 'image', 'media', 'other']}}); rid += 1
json.dump(arules, open(os.path.join(D, 'extension', 'rules_adult.json'), 'w'), separators=(',', ':'))
shutil.copyfile(os.path.join(A, 'NOTICE.txt'), os.path.join(D, 'extension', 'THIRD_PARTY_NOTICES.txt'))
# Android app: bundled asset (the app reads it only when the family filter is on)
aa = os.path.join(D, 'android', 'app', 'src', 'main', 'assets')
open(os.path.join(aa, 'adult.txt'), 'w').write('\n'.join(adult) + '\n')
shutil.copyfile(os.path.join(A, 'NOTICE.txt'), os.path.join(aa, 'THIRD_PARTY_NOTICES.txt'))
print('adult domains', len(adult), 'extension rules', len(arules))

# ---------- family filter: anti-bypass (optional, OFF by default; hand-curated human-override/bypass/source.txt) ----------
B = os.path.join(D, 'bypass')
bypass = sorted({l.strip() for l in open(os.path.join(B, 'source.txt')) if l.strip() and not l.startswith('#') and DOM.match(l.strip())})
NEVER_B = {'cloudflare.com', 'amazonaws.com', 'proton.me', 'google.com', 'adguard-dns.com', 'microsoft.com', 'apple.com'}
assert not (set(bypass) & NEVER_B), set(bypass) & NEVER_B
bhead = ['Mindveto anti-bypass list: web proxies, VPN services, Tor and secure-DNS addresses (https://mindveto.app/)',
         f'Updated: {today}  Domains: {len(bypass)}', 'Optional list, hand-curated by Mindveto. (c) 2026 Amghar Said, free to use in your own filter.']
open(os.path.join(B, 'domains.txt'), 'w').write('\n'.join('# ' + h for h in bhead) + '\n' + '\n'.join(bypass) + '\n')
open(os.path.join(B, 'hosts.txt'), 'w').write('\n'.join('# ' + h for h in bhead) + '\n' + '\n'.join(f'0.0.0.0 {d}\n0.0.0.0 www.{d}' for d in bypass) + '\n')
open(os.path.join(B, 'adblock.txt'), 'w').write('! Title: Mindveto anti-bypass\n' + '\n'.join('! ' + h for h in bhead) + '\n' + '\n'.join(f'||{d}^' for d in bypass) + '\n')
brules = [{'id': 1, 'priority': 1, 'action': {'type': 'redirect', 'redirect': {'extensionPath': '/blocked.html?f=bypass'}},
           'condition': {'requestDomains': bypass, 'resourceTypes': ['main_frame']}},
          {'id': 2, 'priority': 1, 'action': {'type': 'block'},
           'condition': {'requestDomains': bypass, 'resourceTypes': ['sub_frame', 'script', 'xmlhttprequest', 'websocket', 'image', 'media', 'other']}}]
json.dump(brules, open(os.path.join(D, 'extension', 'rules_bypass.json'), 'w'), separators=(',', ':'))
open(os.path.join(aa, 'bypass.txt'), 'w').write('\n'.join(bypass) + '\n')
print('bypass domains', len(bypass))

# ---------- family filter: gambling + dating (optional, OFF by default) ----------
# gamble/gamble.txt is built by tools/build_ho_gamble.py (MIT list + own additions); dating/source.txt is hand-curated.
EXTRA = {'gamble': ('gamble.txt', 'Mindveto family filter: gambling, betting and casino sites (https://mindveto.app/)',
                    'Optional list. Sinfonietta/hostfiles gambling-hosts (MIT, (c) 2016 Sinfonietta) + own additions.'),
         'dating': ('source.txt', 'Mindveto family filter: dating apps and random video chat (https://mindveto.app/)',
                    'Optional list, hand-curated by Mindveto. (c) 2026 Amghar Said, free to use in your own filter.')}
NEVER_X = {'google.com', 'youtube.com', 'facebook.com', 'instagram.com', 'snapchat.com', 'apple.com', 'microsoft.com', 'paypal.com'}
for key, (src, title, note) in EXTRA.items():
    X = os.path.join(D, key)
    xs = sorted({l.strip() for l in open(os.path.join(X, src)) if l.strip() and not l.startswith('#') and DOM.match(l.strip())})
    assert not (set(xs) & NEVER_X), set(xs) & NEVER_X
    xhead = [title, f'Updated: {today}  Domains: {len(xs)}', note]
    open(os.path.join(X, 'domains.txt'), 'w').write('\n'.join('# ' + h for h in xhead) + '\n' + '\n'.join(xs) + '\n')
    open(os.path.join(X, 'hosts.txt'), 'w').write('\n'.join('# ' + h for h in xhead) + '\n' + '\n'.join(f'0.0.0.0 {d}\n0.0.0.0 www.{d}' for d in xs) + '\n')
    open(os.path.join(X, 'adblock.txt'), 'w').write(f'! Title: {title}\n' + '\n'.join('! ' + h for h in xhead) + '\n' + '\n'.join(f'||{d}^' for d in xs) + '\n')
    xrules = [{'id': 1, 'priority': 1, 'action': {'type': 'redirect', 'redirect': {'extensionPath': f'/blocked.html?f={key}'}},
               'condition': {'requestDomains': xs, 'resourceTypes': ['main_frame']}},
              {'id': 2, 'priority': 1, 'action': {'type': 'block'},
               'condition': {'requestDomains': xs, 'resourceTypes': ['sub_frame', 'script', 'xmlhttprequest', 'websocket', 'image', 'media', 'other']}}]
    json.dump(xrules, open(os.path.join(D, 'extension', f'rules_{key}.json'), 'w'), separators=(',', ':'))
    open(os.path.join(aa, f'{key}.txt'), 'w').write('\n'.join(xs) + '\n')
    print(key, 'domains', len(xs))
# one notices file for everything we ship from third-party lists
notice = open(os.path.join(A, 'NOTICE.txt')).read().rstrip('\n') + (
    '\n\nThe gambling list uses Sinfonietta/hostfiles gambling-hosts (MIT License, (c) 2016 Sinfonietta), same license text as above.\n')
for dst in (os.path.join(D, 'extension', 'THIRD_PARTY_NOTICES.txt'), os.path.join(aa, 'THIRD_PARTY_NOTICES.txt'), os.path.join(D, 'gamble', 'NOTICE.txt')):
    open(dst, 'w').write(notice)

# ---------- download zips (kept in sync with the lists) ----------
import zipfile
def mkzip(name, files):
    with zipfile.ZipFile(os.path.join(D, name), 'w', zipfile.ZIP_DEFLATED) as z:
        for arc, src in files: z.write(src, arc)
lic = os.path.join(D, 'extension', 'LICENSE.txt'); pc = os.path.join(D, 'pc'); hosts = os.path.join(D, 'hosts.txt')
ah = os.path.join(A, 'hosts.txt'); an = os.path.join(D, 'extension', 'THIRD_PARTY_NOTICES.txt')
mkzip('human-override-windows.zip', [('Start-Mindveto.bat', os.path.join(pc, 'Start-Mindveto.bat')), ('Mindveto.ps1', os.path.join(pc, 'Mindveto.ps1')),
      ('hosts.txt', hosts), ('adult-hosts.txt', ah), ('bypass-hosts.txt', os.path.join(B, 'hosts.txt')), ('gamble-hosts.txt', os.path.join(D, 'gamble', 'hosts.txt')), ('dating-hosts.txt', os.path.join(D, 'dating', 'hosts.txt')), ('THIRD_PARTY_NOTICES.txt', an), ('LICENSE.txt', lic), ('README-WINDOWS.txt', os.path.join(pc, 'README-WINDOWS.txt'))])
mkzip('human-override-mac-linux.zip', [('mindveto.sh', os.path.join(pc, 'mindveto.sh')), ('hosts.txt', hosts), ('adult-hosts.txt', ah), ('bypass-hosts.txt', os.path.join(B, 'hosts.txt')), ('gamble-hosts.txt', os.path.join(D, 'gamble', 'hosts.txt')), ('dating-hosts.txt', os.path.join(D, 'dating', 'hosts.txt')), ('THIRD_PARTY_NOTICES.txt', an), ('LICENSE.txt', lic),
      ('README-MAC-LINUX.txt', os.path.join(pc, 'README-MAC-LINUX.txt'))])
mkzip('human-override-pro-pack.zip', [(f, os.path.join(P, f)) for f in sorted(os.listdir(P)) if f != 'LICENSE.txt'] + [('LICENSE.txt', lic)])
print('zips ok')

# ---------- browser extension: paste guard sites + versioned zip ----------
# The paste guard content script only runs on AI chat, search, writing and coding sites (never on other pages).
mf_path = os.path.join(D, 'extension', 'manifest.json')
MF = json.load(open(mf_path))
guard = sorted({d for k in ('chat', 'search', 'writing', 'coding') for d in L['categories'].get(k, {}).get('domains', []) if DOM.match(d)})
gpaths = sorted({p for k in ('chat', 'search', 'writing', 'coding') for p in L['categories'].get(k, {}).get('paths', [])})
MF['content_scripts'] = [{'matches': [f'*://*.{d}/*' for d in guard] + [f'*://*.{p}*' for p in gpaths], 'js': ['detect.js', 'paste.js'], 'run_at': 'document_start'}]
json.dump(MF, open(mf_path, 'w'), indent=2, ensure_ascii=False); open(mf_path, 'a').write('\n')
ext = os.path.join(D, 'extension'); zname = f"human-override-{MF['version']}.zip"
for old in os.listdir(D):
    if re.fullmatch(r'human-override-\d+\.\d+\.\d+\.zip', old) and old != zname: os.remove(os.path.join(D, old))
with zipfile.ZipFile(os.path.join(D, zname), 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(ext):
        dirs[:] = [d for d in dirs if d != '_metadata']   # created by Chrome when the folder is loaded unpacked
        for f in sorted(files):
            p = os.path.join(root, f); z.write(p, os.path.relpath(p, ext))
print('extension zip', zname, 'paste guard sites', len(guard))
