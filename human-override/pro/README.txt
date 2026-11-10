HUMAN OVERRIDE PRO PACK - the AI kill switch for organisations
(c) 2026 Amghar Said. All rights reserved. Human Override - the AI kill switch. https://geopolcoins.xyz/human-override.html

For IT departments of courts, police, government, schools and companies that must keep AI chatbots and AI tools
off their network and devices. Domains: 145. Updated: 2026-11-10. Fresh copies: https://geopolcoins.xyz/human-override/pro/

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
