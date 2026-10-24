#!/usr/bin/env python3
# Builds privacy.html, cookies.html and legal.html. Usage: python3 tools/build_legal.py "Name" "Address" "email" "KBO (optional)"
import sys
import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')+'/'
UPDATED='24 October 2026'
# Operator details: fill these in once, then rebuild. Empty = shows a visible placeholder.
OP_NAME=sys.argv[1] if len(sys.argv)>1 else ''
OP_ADDR=sys.argv[2] if len(sys.argv)>2 else ''
OP_MAIL=sys.argv[3] if len(sys.argv)>3 else ''
OP_KBO =sys.argv[4] if len(sys.argv)>4 else ''
def f(v,label): return v if v else f'<span class="fill">[{label}]</span>'
NAME=OP_NAME or 'The GEOPOLCOINS / $MAIGA project team'; ADDR=(OP_ADDR+'<br>') if OP_ADDR else ''; MAIL=(f'<a href="mailto:{OP_MAIL}">{OP_MAIL}</a>' if OP_MAIL else f(OP_MAIL,'contact email'))
KBO=(f'Enterprise number (KBO/BCE): {OP_KBO}<br>' if OP_KBO else '')

def page(slug,title,desc,h1,body):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self' 'unsafe-inline'; worker-src 'self'; manifest-src 'self'; style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'none'">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://geopolcoins.xyz/{slug}">
<meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="https://geopolcoins.xyz/{slug}"><meta property="og:image" content="https://geopolcoins.xyz/og-image.jpg"><meta name="twitter:card" content="summary">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><meta name="theme-color" content="#050b1b">
<style>
:root{{--bg:#050b1b;--panel:#0b1a35;--text:#f4f7ff;--dim:#c3cfe4;--gold:#ffd800;--line:rgba(169,212,255,.25)}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,Segoe UI,Roboto,sans-serif}}
main{{max-width:860px;margin:0 auto;padding:16px 16px 60px}}a{{color:var(--gold)}}
.skip{{position:absolute;left:8px;top:-60px;background:var(--gold);color:#000;padding:10px 14px;border-radius:8px;font-weight:800}}.skip:focus{{top:8px}}
.top{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;font-size:14px}}.top a{{display:inline-block;padding:6px 0}}
h1{{font-size:clamp(28px,5vw,40px);line-height:1.15;margin:18px 0 4px}}h2{{font-size:21px;margin:30px 0 6px;color:var(--gold)}}h3{{font-size:17px;margin:18px 0 4px}}
p,li{{color:var(--dim)}}strong{{color:#fff}}
.upd{{color:var(--dim);font-size:14px}}
.box{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin:14px 0}}
.tbl{{overflow-x:auto;margin:10px 0}}table{{border-collapse:collapse;width:100%;font-size:14px;min-width:560px}}th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}}th{{background:var(--panel);color:#fff}}td{{color:var(--dim)}}
code{{background:#071226;padding:1px 5px;border-radius:5px;font-size:13px;color:#fff}}
.fill{{background:#ff4b61;color:#fff;padding:0 6px;border-radius:5px;font-weight:700}}
.toc{{columns:2;font-size:14px}}@media(max-width:600px){{.toc{{columns:1}}}}
footer{{text-align:center;color:var(--dim);font-size:13px;margin-top:40px}}footer a{{display:inline-block;padding:6px 2px}}
</style></head><body>
<a class="skip" href="#main">Skip to content</a>
<main id="main">
<div class="top"><a href="/">&larr; geopolcoins.xyz</a><nav aria-label="Legal"><a href="privacy.html">Privacy</a> · <a href="cookies.html">Cookies</a> · <a href="legal.html">Legal notice</a> · <a href="/#terms">Terms</a></nav></div>
<h1>{h1}</h1>
<p class="upd">Last updated: {UPDATED}. The English text is the reference version. <span lang="nl">Nederlands: vragen in het Nederlands zijn welkom.</span> <span lang="fr">Français : questions en français bienvenues.</span></p>
{body}
<footer>© 2026 $MAIGA • <a href="/">HOME</a> • <a href="privacy.html">PRIVACY</a> • <a href="cookies.html">COOKIES</a> • <a href="legal.html">LEGAL NOTICE</a> • <a href="/#terms">TERMS</a></footer>
</main>
<script src="pwa.js" defer></script>
</body></html>
'''

privacy=f'''
<div class="box"><strong>In short:</strong> we collect as little as possible. No cookies, no ad trackers, no selling of data, no profiles. Most tools run only in your browser. We only store what you choose to send us (for example a score, a nickname, a public post or a request for a custom bot), and the anonymous visit counter knows only page, day and the website you came from. We never ask for your seed phrase, private keys or passwords.</div>
<nav aria-label="Contents"><ol class="toc">
<li><a href="#who">Who is responsible</a></li><li><a href="#what">What we collect and why</a></li><li><a href="#device">What stays on your device</a></li><li><a href="#third">Services that receive data from your browser</a></li><li><a href="#share">Who we share data with</a></li><li><a href="#transfer">International transfers</a></li><li><a href="#keep">How long we keep data</a></li><li><a href="#rights">Your rights (worldwide)</a></li><li><a href="#us">California and other US states</a></li><li><a href="#kids">Children</a></li><li><a href="#chain">Blockchain data</a></li><li><a href="#security">Security</a></li><li><a href="#changes">Changes</a></li></ol></nav>

<h2 id="who">1. Who is responsible</h2>
<p>The controller of your personal data (the one who decides why and how it is used) is:</p>
<p class="box">{NAME}<br>{ADDR}{KBO}Email: {MAIL}<br>Website: geopolcoins.xyz</p>
<p>The project is run by a small team currently based in Morocco, so Moroccan Law 09-08 on the protection of personal data applies to our processing; the Moroccan supervisory authority is the CNDP (cndp.ma). Our visitors are mainly in the United States and other countries worldwide. Because the site is also used by people in the EU and the UK, we also follow the EU and UK GDPR. We have not appointed an EU representative, because our processing is occasional, small-scale and unlikely to put your rights at risk (Art. 27(2) GDPR); this may change if the project grows. We have no data protection officer because we do not process data on a large scale. For any privacy question or request, email us at the address above.</p>

<h2 id="what">2. What we collect and why</h2>
<div class="tbl"><table>
<tr><th>Feature</th><th>Data</th><th>Why</th><th>Legal basis (GDPR)</th></tr>
<tr><td>Visit counter (all main pages)</td><td>Page name, day, and the website you came from (only the domain, for example <code>x.com</code>). No cookies, no IP address, no device or user ID.</td><td>See which tools are used.</td><td>Not personal data. Where any law treats it as such: legitimate interest (Art. 6(1)(f)).</td></tr>
<tr><td>Games and tournament</td><td>Pilot name you choose, scores, game type, date; optionally the wallet address you enter for prizes.</td><td>Leaderboards, tournament results and prize payouts.</td><td>Taking part in the game (contract, Art. 6(1)(b)).</td></tr>
<tr><td>Wallet verification (optional)</td><td>Pilot name and the wallet address that signed a free message. The signature is checked; it is not a transaction.</td><td>Reserve your pilot name and prevent impersonation.</td><td>Your request (contract, Art. 6(1)(b)).</td></tr>
<tr><td>Prize wheel and payouts</td><td>Pilot name, wallet address, prize amount, status and transaction ID.</td><td>Pay prizes and keep a record of what was paid. Payout records (receiving wallet, amount, transaction ID) are public on our site as proof of payment, just as they are on the blockchain.</td><td>Contract (Art. 6(1)(b)); keeping records (Art. 6(1)(c)/(f)).</td></tr>
<tr><td>Team board</td><td>Nickname, your role, the role you look for, a short pitch. Contact details and wallets are blocked.</td><td>Public board to find team members.</td><td>Your choice to post (consent, Art. 6(1)(a)); you can ask us to remove it.</td></tr>
<tr><td>Factory Hub and Bot Garage community</td><td>Nickname plus what you share: coin name, ticker, meme text, description, or a bot recipe; likes and copies.</td><td>Show community creations.</td><td>Your choice to share (consent, Art. 6(1)(a)).</td></tr>
<tr><td>Battle of the day</td><td>Vote counts only. We do not store who voted.</td><td>Show the result.</td><td>Not personal data.</td></tr>
<tr><td>Custom bot request form</td><td>Name, email, business name, business type, your message, language.</td><td>Answer your request and prepare an offer.</td><td>Steps before a contract at your request (Art. 6(1)(b)).</td></tr>
<tr><td>Technical logs</td><td>When your browser contacts our database or our web host, they briefly log technical data such as your IP address and browser type.</td><td>Security, abuse prevention, keeping the service running.</td><td>Legitimate interest (Art. 6(1)(f)).</td></tr>
</table></div>
<p>We do not use your data for advertising, we do not build profiles, and we make no automated decisions that have legal or similarly significant effects on you. The Launch Check in the Factory is a word list that runs in your browser; it does not decide anything about you.</p>

<h2 id="device">3. What stays on your device</h2>
<p>Many tools work only in your browser and keep their settings in your browser's local storage on your own device. We cannot see this data. Examples: language choice, your saved bots, recent token checks, game best scores, and, only if you choose "remember", your own AI key. See the <a href="cookies.html">Cookie and storage policy</a> for the full list and how to delete it.</p>
<p><strong>Your AI key</strong> (Meme Factory, Bot Garage): it is sent directly from your browser to the AI provider you pick (Anthropic, OpenAI or OpenRouter), never to us. Your idea or prompt then goes to that provider under its own privacy policy, and that provider bills you.</p>
<p><strong>Meme Studio</strong>: your photo and your meme are made on your device and are not uploaded to us.</p>

<h2 id="third">4. Services that receive data from your browser</h2>
<p>Some features load data from, or send you to, independent services. When that happens, your browser connects to them directly and they can see your IP address and browser details under their own privacy policies:</p>
<ul>
<li><strong>GeckoTerminal</strong> (coin info, trending list, Token Checkup): we request public token data.</li>
<li><strong>memegen.link</strong> (classic meme templates in the Meme Studio and Factory).</li>
<li><strong>Jupiter</strong> (swap widget on the home page): its script loads on the home page; swaps are signed in your own wallet.</li>
<li><strong>Phantom or your wallet</strong>: only when you choose to connect or sign.</li>
<li><strong>Ko-fi</strong>: tips and digital products are sold and paid through Ko-fi, which handles payment data as its own controller. We receive the order details Ko-fi gives sellers (such as name, email and what you bought) to deliver and support your purchase.</li>
<li><strong>Discord, X, Pump.fun, Solscan, DexScreener and other links</strong>: only when you click them.</li>
</ul>

<h2 id="share">5. Who we share data with</h2>
<p>We do not sell or rent personal data, and we do not share it for advertising. We use these service providers (processors), which process data only on our instructions:</p>
<ul>
<li><strong>Supabase</strong> (database, hosted in the EU, Frankfurt): stores the data in section 2.</li>
<li><strong>GitHub Pages</strong> (GitHub Inc., USA): hosts the website and keeps short technical logs.</li>
</ul>
<p>Public posts (leaderboards with pilot names and scores, team board, Factory Hub, community bots) are visible to everyone. Our Discord helper posts game standings (names and scores only, never wallets). We may disclose data if the law requires it, or to protect our rights or others' safety.</p>

<h2 id="transfer">6. International transfers</h2>
<p>We work from Morocco. Our database is in the European Union and our web host GitHub is in the United States. Transfers from Morocco follow Law 09-08. For data from the EU/UK, transfers rely on the EU-US Data Privacy Framework and/or the European Commission's Standard Contractual Clauses. Third-party services in section 4 may process data in other countries under their own safeguards.</p>

<h2 id="keep">7. How long we keep data</h2>
<div class="tbl"><table>
<tr><th>Data</th><th>Kept</th></tr>
<tr><td>Visit counts</td><td>Totals per page and day, no personal data; kept as statistics.</td></tr>
<tr><td>Team board posts</td><td>Shown for 14 days.</td></tr>
<tr><td>Factory Hub packs</td><td>Shown for 30 days.</td></tr>
<tr><td>Scores, pilot names, verified wallets, community bots</td><td>As long as the leaderboard or feature exists, or until you ask us to delete them.</td></tr>
<tr><td>Prize and payout records</td><td>Up to 7 years where accounting or tax rules require. The public payout list can be removed from our site on request; the blockchain record stays.</td></tr>
<tr><td>Custom bot requests</td><td>At most 12 months, or less if you ask.</td></tr>
<tr><td>Technical logs (host, database)</td><td>Short periods set by the provider (usually days to weeks).</td></tr>
</table></div>
<p>Data on a public blockchain cannot be deleted; see section 11.</p>

<h2 id="rights">8. Your rights (worldwide)</h2>
<p>Wherever you live, you can ask us to:</p>
<ul>
<li><strong>access</strong> the personal data we hold about you and get a copy (portability);</li>
<li><strong>correct</strong> it;</li>
<li><strong>delete</strong> it ("right to be forgotten");</li>
<li><strong>restrict</strong> or <strong>object to</strong> its use, including any use based on legitimate interest;</li>
<li><strong>withdraw consent</strong> at any time (for example remove your public post), without affecting earlier use.</li>
</ul>
<p>Email us at {MAIL} and tell us your pilot name, nickname or email so we can find your data. We may ask for proof that the data is yours (for example a signed message from the same wallet). We answer within one month (extendable by two months for complex requests, as the GDPR allows) and free of charge.</p>
<p>If you think we got it wrong, you can complain to a data protection authority: the authority in the country where you live or work (for example the CNDP in Morocco, any EU data protection authority, the ICO in the UK, the ANPD in Brazil, the Office of the Privacy Commissioner in Canada or the OAIC in Australia). We would appreciate the chance to fix it first.</p>
<p>These rights follow Moroccan Law 09-08, the EU and UK GDPR, Brazil's LGPD, Canada's PIPEDA, Switzerland's FADP, Australia's Privacy Act, Japan's APPI, Singapore's PDPA, South Korea's PIPA, India's DPDP Act and similar laws. We give the same rights to everyone, wherever you live.</p>

<h2 id="us">9. United States (California and other states)</h2>
<p>Under the California Consumer Privacy Act (as amended by the CPRA) and similar state laws: in the last 12 months we collected the categories in section 2 (identifiers such as a nickname, email or wallet address; commercial information for Ko-fi orders; internet activity limited to technical logs), for the purposes in section 2. <strong>We do not sell or share personal information</strong> for cross-context behavioral advertising and we do not use sensitive personal information to infer characteristics. You have the right to know, delete and correct your personal information, and we will not discriminate against you for using these rights. We honor Global Privacy Control signals, although we do no tracking that they would stop. Send requests to {MAIL}; we answer within 45 days. Residents of other US states with privacy laws (for example Virginia, Colorado, Connecticut, Utah, Texas and Oregon) have similar rights to access, correct, delete and opt out, and can use the same email; if we decline a request you may appeal by replying to our answer. We do not send marketing emails; we only email you to answer your own request or about your purchase (US CAN-SPAM and similar laws).</p>

<h2 id="kids">10. Children</h2>
<p>This site is not meant for children. You must be at least 16 to use features that store data (or the minimum age for consent in your country, if higher), and 18 or the age of majority to take part in tournaments or prizes. We do not knowingly collect data from children under 13 (US COPPA) or under 16. If you believe a child has sent us data, email us and we will delete it.</p>

<h2 id="chain">11. Blockchain data</h2>
<p>Prize payouts and swaps happen on the public Solana blockchain. Wallet addresses and transactions there are public and permanent, and nobody (including us) can change or delete them. Apart from payout records, which we publish as proof of payment, we do not show wallet addresses on our site. Anyone can look up a transaction on the blockchain.</p>

<h2 id="security">12. Security</h2>
<p>We use encrypted connections (HTTPS), strict database access rules (row level security), rate limits, automatic secret scanning and code scanning. Only the admin account can read custom bot requests and the wallet addresses entered for prizes or verification. Payout records are public by design (see section 11). No system is perfectly secure; if a breach affects your rights, we will tell the authority and, where required, you, within the legal deadlines.</p>

<h2 id="changes">13. Changes</h2>
<p>We update this policy when the site changes. The date at the top shows the latest version. Important changes will also be mentioned on the home page.</p>
'''

cookies=f'''
<div class="box"><strong>In short:</strong> geopolcoins.xyz does not set cookies and uses no analytics or advertising trackers. That is why there is no cookie banner. Some tools save settings in your browser's local storage, only to do what you asked for.</div>

<h2>1. Cookies</h2>
<p>Our own pages set <strong>no cookies</strong>. Our visit counter works without cookies and without storing any identifier on your device.</p>

<h2>2. Local storage on your device</h2>
<p>Local storage is a small storage area in your browser. Our pages use it only for functions you use. The data stays on your device and is not sent to us. Under the EU ePrivacy rules this storage is allowed without consent because it is strictly necessary for a service you request.</p>
<div class="tbl"><table>
<tr><th>Name (key)</th><th>Purpose</th><th>Kept</th></tr>
<tr><td><code>maiga_lang</code></td><td>Your language choice.</td><td>Until you clear it.</td></tr>
<tr><td><code>maiga_garage_bots_v1</code></td><td>Bots you saved in the Bot Garage ("My bots").</td><td>Until you delete them.</td></tr>
<tr><td><code>maiga_factory_ai_v1</code></td><td>Your AI key and model, only if you tick "remember" (Factory and Garage).</td><td>Until you press "Forget key" or clear it.</td></tr>
<tr><td><code>maiga_factory_calls_&lt;date&gt;</code></td><td>How many AI calls you made today, so your daily limit works.</td><td>Per day.</td></tr>
<tr><td><code>maiga_factory_share</code>, <code>maiga_tm_last</code></td><td>Remembers your last share or post, to prevent double posting.</td><td>Until you clear it.</td></tr>
<tr><td><code>maiga_flappy_best</code>, <code>maiga_total_…</code></td><td>Your best game scores and daily totals.</td><td>Until you clear it.</td></tr>
<tr><td>Token Checkup history</td><td>Your recent token checks.</td><td>Until you clear it.</td></tr>
<tr><td>App cache (service worker)</td><td>Saves copies of our own pages and images so the app opens fast and works offline. It never stores other websites.</td><td>Replaced at each update.</td></tr>
<tr><td>Admin login (admin page only)</td><td>Keeps the site admin logged in.</td><td>Until logout.</td></tr>
</table></div>
<p>Names can change when we improve a tool; the purposes stay the same.</p>

<h2>3. Third parties</h2>
<p>The swap widget on the home page is loaded from <strong>Jupiter</strong> and may use its own storage under Jupiter's policy. When you click a link to another site (Ko-fi, Discord, X, Pump.fun, Solscan, DexScreener and others), that site's own cookies and policies apply. Images from memegen.link and data from GeckoTerminal are loaded without cookies from our side.</p>

<h2>4. How to delete it</h2>
<p>You can delete all stored data at any time in your browser settings (look for "site data", "cookies and site data" or "clear browsing data" for geopolcoins.xyz). If you installed the app, uninstalling it also removes its storage. Deleting it removes your saved bots and settings.</p>

<h2>5. Questions</h2>
<p>See our <a href="privacy.html">Privacy policy</a> or email {MAIL}.</p>
'''

legal=f'''
<h2>Operator</h2>
<p class="box">{NAME}<br>{ADDR}{KBO}Email: {MAIL}<br>Website: geopolcoins.xyz</p>
<p>The team is currently based in Morocco. Hosting: GitHub Pages, GitHub Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, USA. Database: Supabase (EU, Frankfurt).</p>

<h2>What this site is</h2>
<p>$MAIGA and GEOPOLCOINS are satirical entertainment and meme projects, with free tools and games. <strong>Nothing on this site is financial, investment, legal or tax advice</strong>, and nothing is an offer or a solicitation to buy or sell any token or financial product. We do not issue, sell or hold tokens for you through this site, we do not provide lending, custody or exchange services, and we never ask for your seed phrase or private keys. Swaps on the home page run through Jupiter directly from your own wallet. Crypto assets are highly risky and you can lose everything.</p>
<p>Nothing on this site is an offer or sale of securities, and nothing has been registered with or approved by the US Securities and Exchange Commission or any other regulator. The site is not directed at people in countries where its content or crypto-assets are prohibited, and it may not be used by anyone in, or ordinarily resident in, a country or region under comprehensive sanctions (for example by the UN, the EU, the UK or the US OFAC), or by anyone on a sanctions list. You are responsible for following the laws where you live. Tournaments and prizes are free to enter, never require a purchase, and are open only to adults where this is allowed.</p>

<h2>Satire, names and images</h2>
<p>The site uses parody and satire. Our characters are original pixel art and do not depict real people. Classic meme templates in the Meme Studio come from the open-source memegen project (MIT licence) and memegen.link; the pictures belong to their respective owners and are shown for parody, commentary and personal use. You are responsible for the images, names and words you create and publish.</p>

<h2>Report content or rights problems</h2>
<p>People can post short texts in the team board, the Factory Hub and the Bot Garage community. If you see illegal content, a rights infringement (for example copyright or trademark) or content about you, email {MAIL} with the link or the exact text, why you think it is a problem, and your contact details. We review notices quickly, remove content where needed and tell the poster when appropriate. This is our point of contact under the EU Digital Services Act; you may write to us in English, Dutch or French.</p>

<h2>Digital products</h2>
<p>Digital products in our Ko-fi shop are sold through Ko-fi. The product page describes what you get. For EU consumers: by asking for immediate download, you agree that the 14-day right of withdrawal ends once the download starts. If a file is broken or not as described, email us and we will fix it or refund you. Buying a product gives no tokens, rights or returns.</p>

<h2>Liability</h2>
<p>The site and its tools are provided "as is" and may contain mistakes or be unavailable. To the extent the law allows, we are not liable for losses from using this site or linked third-party services. Nothing in these texts limits rights you have under mandatory consumer law where you live.</p>

<h2>Applicable law</h2>
<p>If you have a problem, email us first and we will try to solve it quickly and fairly. Nothing in these texts takes away the protection that the mandatory consumer and privacy laws of the country where you live give you. See also our <a href="/#terms">Terms and disclaimers</a>, <a href="privacy.html">Privacy policy</a> and <a href="cookies.html">Cookie policy</a>.</p>
'''

open(OUT+'privacy.html','w').write(page('privacy.html','Privacy policy | $MAIGA geopolcoins.xyz','How geopolcoins.xyz handles personal data: what we collect, why, how long, and your rights under GDPR, CCPA and other laws. No cookies, no trackers.','Privacy policy',privacy))
open(OUT+'cookies.html','w').write(page('cookies.html','Cookie policy | $MAIGA geopolcoins.xyz','geopolcoins.xyz sets no cookies and uses no trackers. This page lists the local storage our tools use and how to delete it.','Cookie and storage policy',cookies))
open(OUT+'legal.html','w').write(page('legal.html','Legal notice | $MAIGA geopolcoins.xyz','Who runs geopolcoins.xyz, how to contact us, how to report content, and important legal information about this satirical meme project.','Legal notice',legal))
print('ok', 'placeholders' if not OP_NAME else 'filled')
