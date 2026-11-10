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

# ---------- Pro pack for IT departments (justice, government, schools, companies) ----------
P = os.path.join(D, 'pro'); os.makedirs(P, exist_ok=True)
paths = sorted({p for c in L['categories'].values() for p in c.get('paths', [])})
cr = '(c) 2026 Amghar Said. All rights reserved. Human Override - the AI kill switch. https://geopolcoins.xyz/human-override.html'
pats = [f'{d}' for d in doms] + paths
json.dump({"_comment": "Chrome and Edge enterprise policy (GPO/Intune/Jamf/Google Admin). " + cr,
           "URLBlocklist": pats}, open(os.path.join(P, 'chrome-edge-policy.json'), 'w'), indent=1)
json.dump({"_comment": cr, "policies": {"WebsiteFilter": {"Block": [f"*://*.{d}/*" for d in doms] + [f"*://{d}/*" for d in doms] + [f"*://{p}*" for p in paths] + [f"*://*.{p}*" for p in paths]}}},
          open(os.path.join(P, 'firefox-policies.json'), 'w'), indent=1)
open(os.path.join(P, 'rpz.zone'), 'w').write(f'; Human Override RPZ zone for BIND / PowerDNS / Infoblox / Knot. {cr}\n$TTL 300\n@ IN SOA localhost. root.localhost. ({today.replace("-", "")}01 3600 600 86400 300)\n@ IN NS localhost.\n' +
    ''.join(f'{d} CNAME .\n*.{d} CNAME .\n' for d in doms))
open(os.path.join(P, 'unbound.conf'), 'w').write(f'# Human Override for Unbound / OPNsense / pfSense. {cr}\nserver:\n' + ''.join(f'  local-zone: "{d}." always_nxdomain\n' for d in doms))
open(os.path.join(P, 'dnsmasq.conf'), 'w').write(f'# Human Override for dnsmasq / OpenWrt / Pi-hole (custom dnsmasq). {cr}\n' + ''.join(f'address=/{d}/0.0.0.0\n' for d in doms))
open(os.path.join(P, 'squid-acl.conf'), 'w').write(f'# Human Override for Squid proxy. {cr}\nacl human_override_ai dstdomain ' + ' '.join('.' + d for d in doms) + '\nhttp_access deny human_override_ai\n')
open(os.path.join(P, 'firewall-edl.txt'), 'w').write(''.join(f'{d}\n*.{d}\n' for d in doms))
ps = [f'# Human Override for Windows Server DNS (run as administrator on the DNS server). {cr}',
      '# Adds DNS query resolution policies that refuse AI domains for all clients.',
      '# Remove with: Get-DnsServerQueryResolutionPolicy | Where-Object Name -like "HumanOverrideAI*" | ForEach-Object { Remove-DnsServerQueryResolutionPolicy -Name $_.Name -Force }',
      'Get-DnsServerQueryResolutionPolicy -ErrorAction SilentlyContinue | Where-Object Name -like "HumanOverrideAI*" | ForEach-Object { Remove-DnsServerQueryResolutionPolicy -Name $_.Name -Force }']
for i in range(0, len(doms), 20):
    part = doms[i:i + 20]
    crit = 'EQ,' + ','.join(f'*.{d},{d}' for d in part)
    ps.append(f"Add-DnsServerQueryResolutionPolicy -Name 'HumanOverrideAI{i // 20 + 1}' -Action DENY -FQDN '{crit}' -ProcessingOrder {i // 20 + 1}")
ps.append('Write-Host "Human Override: AI domains are now refused by this DNS server."')
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

Terms of use (provided "as is", limits of liability): https://geopolcoins.xyz/human-override-terms.html
Human Override Pro (help with roll-out, custom lists, weekly reports): https://geopolcoins.xyz/human-override.html#pro
''')
print('pro pack files', len(os.listdir(P)))

# ---------- download zips (kept in sync with the lists) ----------
import zipfile
def mkzip(name, files):
    with zipfile.ZipFile(os.path.join(D, name), 'w', zipfile.ZIP_DEFLATED) as z:
        for arc, src in files: z.write(src, arc)
lic = os.path.join(D, 'extension', 'LICENSE.txt'); pc = os.path.join(D, 'pc'); hosts = os.path.join(D, 'hosts.txt')
mkzip('human-override-windows.zip', [('Start-HumanOverride.bat', os.path.join(pc, 'Start-HumanOverride.bat')), ('HumanOverride.ps1', os.path.join(pc, 'HumanOverride.ps1')),
      ('hosts.txt', hosts), ('LICENSE.txt', lic), ('README-WINDOWS.txt', os.path.join(pc, 'README-WINDOWS.txt'))])
mkzip('human-override-mac-linux.zip', [('human-override.sh', os.path.join(pc, 'human-override.sh')), ('hosts.txt', hosts), ('LICENSE.txt', lic),
      ('README-MAC-LINUX.txt', os.path.join(pc, 'README-MAC-LINUX.txt'))])
mkzip('human-override-pro-pack.zip', [(f, os.path.join(P, f)) for f in sorted(os.listdir(P)) if f != 'LICENSE.txt'] + [('LICENSE.txt', lic)])
print('zips ok')
