# Handoff (short) — state 18 Nov 2026

Loaded automatically through `CLAUDE.md`. Rules, owner and git/SQL workflow: `maiga-ops` skill.
Read other files only when the task needs them. Update this file after every larger task (keep it under ~50 lines).
Code map: graphify (Apache-2.0, pinned 0.9.106) builds `graphify-out/` at session start (`tools/graphify_session.sh`,
local AST only, git-ignored). Use `graphify query|explain|path` before grep/read; `graphify update .` after edits.

## Release checklist
- `python3 tools/seo_enhance.py`, `tools/seo_audit.py`, `tools/security_audit.py` → 0 problems.
- Bump `VERSION` in `sw.js` (now `maiga-2026-11-18a`).
- Legal: `python3 tools/build_legal.py "" "" "hello@geopolcoins.xyz"` (owner OK 11 Nov; never his private
  address), then `seo_enhance.py` again.
- Blog: `tools/blog_posts*.py` → `python3 tools/build_blog.py` (title ≤60, description 120-160).
- Extension changes: `python3 tools/build_ho_lists.py` (zip + content-script matches), then
  `git checkout` the 3 other HO zips (only timestamps change). Tests: `node --test human-override/test/detect.test.js`.

## Human Override (main product, © 2026 Amghar Said; birthplace never published)
Page `/human-override.html`, terms `/human-override-terms.html`. Code in `human-override/`:
extension 1.8.0 = **Mindveto** (renamed 12 Nov; hosts/registry markers still "Human Override" so old installs can be undone; Android package id unchanged; optional `social` category, OFF by default, extension-only, never in hosts/DNS lists, not forced by exam mode; test `test/e2e/social_media.py`) (`extension/`: paste guard + own words, approved-AI picker (services in bundled lists.json only),
class + exam mode, tamper log, PIN, schedule + school holidays (skip/only, 8 regions BE/NL/FR, dates ONLY from the
bundled list: `python3 tools/build_ho_holidays.py <clone of openpotato/openholidaysapi.data>`, ODbL, refresh yearly;
BE German community has no data yet); lists in `extension/lists.json`),
Android (`android/`: tamper alerts, target SDK 36, CI builds APK + .aab), Windows `pc/Mindveto.ps1`,
Mac/Linux `pc/mindveto.sh`. Promo video live: https://youtu.be/c-_Isw8tUY8 (10 Nov).
Anonymous counter (site_views): `ho` = page visits; `ho_ext/ho_android/ho_win/ho_mac/ho_pro` = download clicks.

Open:
1. Pricing — reminder Sat 14 Nov 09:00 Brussels (proposal: Free / Plus €15/yr / Pro €180/yr / Custom).
2. Google Play — owner steps in `docs/google-play.md` (upload key → secrets HO_UPLOAD_*, $25, VPN declaration,
   12 testers × 14 days). Store kit for Chrome/Edge/Firefox in `docs/store-kit/`; owner submits.
   Owner 12 Nov: NO paid accounts for now (no Chrome $5, no Play $25) → only free stores (Firefox AMO, Edge).
   1.3.0 store-ready 12 Nov: addons-linter 0 errors (1 expected warning: service_worker ignored by Firefox), gecko min 140,
   popup/blocked/welcome/paste dialog restyled to Mindveto (bundled Atkinson font, zip ~93 KB), screenshots EN/NL/FR in store-kit.
   Chrome Web Store dashboard does not load in the built-in browser; Claude in Chrome was not connected.
   Firefox AMO: SUBMITTED 12 Nov 17:35 ("Mindveto", slug mindveto-the-ai-kill-switch, Privacy & Security, All Rights
   Reserved), 3 EN screenshots + captions + icon saved; review pending (mail to hello@mindveto.app).
   Firefox AMO 1.6.0 SUBMITTED 13 Nov 07:30 (owner OK; owner picked the zip, AMO CSP blocks scripted upload), release +
   reviewer notes from docs/store-kit, source code = No (rules_*.json are domain lists), listing got a family-filter bullet.
   Edge: Partner Center login works, enrollment form half filled (Belgium + Individual, Mindveto, hello@, site) but NOT
   submitted: Microsoft shows the contact address publicly → owner chose to wait for a business address.
   Office pack done 12 Nov: demo videos + AI policy template live; 3 outreach drafts (NL/FR/EN, no recipients) in
   Gmail geopolcoins1@. Owner 12 Nov: SEND NOTHING until he explicitly says so.
3. Android camera/mic guard + tamper notification not yet tested on a real phone.
4. Teacher exam button is live (11 Nov): page `/human-override-class.html`, SQL `supabase-ho-exam.sql` (RPCs exam_create /
   exam_set / exam_status, table srv.ho_classes, only hashes; brake = 10 classes per device per hour via a hashed IP kept 1 h). Backend work goes on Supabase, not
   the Oracle server (no open ports). Browser tests: `python3 human-override/test/e2e/<name>.py` (shared setup in `common.py`; exam test needs
   `python3 -m http.server 8765` in the repo root).
   Family filter = round 1 DONE 12 Nov (1.4.0, free, opt-in, NOT in any store yet: owner decides): adult sites (63.8k domains,
   MIT lists only, `tools/build_ho_adult.py` + NOTICE) + SafeSearch (Google/Bing/DDG/YouTube) in extension, Android, Windows (menu 5/6,
   browser policies with backup), Mac/Linux (`family-on/off`). Test `test/e2e/family_filter.py`.
   Round 2 anti-bypass DONE 13 Nov (1.5.0, not in stores): hand-curated `bypass/source.txt` (88 proxy/VPN/Tor/DoH names,
   own list, no GPL), extension switch, Android switch, PC family-on adds it + DoH off (Chrome/Edge/Firefox policies).
   Round 3 DONE 13 Nov (1.6.0, not in stores, free for now; Plus or not = owner's pricing call): gambling (1,600: Sinfonietta MIT +
   own `gamble/own.txt`, `tools/build_ho_gamble.py`) + dating/random video chat (65, own `dating/source.txt`); separate switches in
   extension + Android; Windows option 5 asks y/n; Mac/Linux `family-on gambling dating`.
   Next features: IT dashboard / central management, AI Act/GDPR report, Human Override Box.
   Never: own VPN, through-wall Wi-Fi surveillance.
   Owner 19 Nov: antivirus/protection is now WANTED as "Mindveto Protect" (complete protect app). Honest scope: no own scan engine; virus scanning is done by the built-in Microsoft Defender, Mindveto adds web protection, warnings and a checkup. Marketing says "Mindveto Protect", never "best antivirus" or "100% safe" (EU misleading-claims rules).

IP protection 18 Nov (free): `LICENSE` at the root of both repos + `human-override/LICENSE.txt` (all rights reserved, lists the
third-party parts: MIT/CC0 lists, OFL font, ODbL holidays); `proof.yml` in both repos stamps SHA-256 lists of the code/site in `proof/`
with OpenTimestamps (daily upgrade); mindveto `archive.yml` saves 28 pages in the Wayback Machine every Monday; takedown kit
`docs/takedown/` (NL guide, EN DMCA + EU DSA notices, form links). Repos stay PUBLIC (free Pages + old installs). Trademark = owner (costs).
Free tool `/password-check.html` (12 Nov): Have I Been Pwned range API, k-anonymity, only 5 hash chars leave the browser.

## Next task: backlink plan mindveto.app (owner asked 16 Nov)
List the 20 best REAL free places for a link (AlternativeTo, Product Hunt, parental-control and AI-in-school lists, etc.),
ready-made text per place (EN, NL/FR where the site is local). Owner wants Claude to post them itself in the built-in
browser: owner makes accounts, types passwords/codes and solves CAPTCHAs; Claude fills the forms; get the owner's OK
per place before clicking Submit/Post. Free places only, no bulk/spam links. Track status per place in this file.
Done 14 Nov on mindveto: download page by situation (child's phone, laptop, Wi-Fi, iPhone note), offices button
"Protect private data in ChatGPT"; privacy check: 0 third-party requests on 170 pages, fonts self-hosted, no cookies.

## Build queue (owner 18 Nov: "maak deze"; one item per new chat, owner pastes the item name)
B1 School starter pack: mindveto.app page (8 langs) with AI policy + parent letter + exam/lesson settings + AI Act art. 4 checklist, printable.
B2 Office "use our AI instead": blocked.html shows "your organisation uses <approved AI>, open it" (from allowSvc) instead of a bare block. Extension.
B3 Shadow-AI count: extension keeps local counts per AI service of blocked tries (no URLs, no content); popup shows top 10; feeds B8.
B4 DONE 18 Nov (extension 1.8.0, not in stores): category `friend` in lists.json (28 companion apps from CC0 aegis ai-adult), on by default, own popup switch; a blocked try logs "AI friend app tried" + red "!" (kind + time only, max 1 line per 5 min). Test `test/e2e/ai_friend.py`. Android/PC: friend domains are in hosts/DNS lists (blocked) but no heads-up there yet.
B5 Lesson switch: exam button gets 3 modes (all AI / approved only / none) per lesson. Supabase: new RPC arg, keep old clients working.
B6 5-minute AI-literacy course: mindveto.app page, 8 langs, 8 short questions, printable certificate made in the browser (no data sent).
B7 Rollout file: page that builds Chrome/Edge policy (.reg + JSON + Intune OMA-URI) to force-install Mindveto with chosen settings;
   extension reads chrome.storage.managed (add managed_schema). Store ID needed for Chrome force-install (no store yet: say so honestly).
B8 AI Act / GDPR proof report: popup button "Print report" opens a local page with settings, allowed AI, paste guard state, B3 counts, date.
B9 Link check + phishing quiz: mindveto.app pages (8 langs). "Is this link safe?" checks a pasted link in the browser only (lookalike/homoglyph and punycode, IP address host, `＠` in URL, URL shorteners, odd TLDs); nothing is sent. Quiz: 8 real AI-phishing tricks (AI-written mail, cloned boss voice, fake login page), "real or fake", printable result. Fits B6 and AI Act art. 4.
B10 Web protection in the extension (1.9.0): new category `threat` with malware/phishing domains from URLhaus (CC0; check license of any other list, MIT/CC0 only), on by default, also in Android/hosts/DNS lists via build_ho_lists.py; plus a local lookalike warning bar ("this is not bol.com") for a small list of big banks/shops/brands. Mind DNR rule limits.
B11 Windows checkup ("Mindveto Protect" for PC): script/app shows in plain words whether Defender real-time protection, firewall and Windows Update are on, and starts a Defender quick scan with one click (`Start-MpScan`), showing the result. Download check: warn on .exe/.apk downloads; optional hash lookup in MalwareBazaar (only the hash leaves the PC, say so in the privacy text). No own engine.
Each: tests, check.py/axe/Lighthouse >= 90 for site work, extension e2e + version bump, privacy text if data handling changes.
Owner 18 Nov: every new feature is ALSO explained on mindveto.app (8 langs; parents/browser-extension pages etc.) and its download bumped. 1.7.0 night mode + 1.8.0 AI friend: done (mindveto#9, #10).

## LinkedIn (owner profile linkedin.com/in/amghar-said-67a95a22)
Profile redone 13 Nov (FR/EN/NL, photo + banner). Plan doc with the first 5 posts: https://claude.ai/artifact/TdHw7eig6NfAbsMz9iozhe.
Post 1 (15 years, People first) by owner 13 Nov; post 2 ("Many parents I talk to...", EN, honest version, no invented
story) posted 17 Nov with owner's OK. Next: posts 3-5 from the doc. Replies to comments: draft, show owner, post after OK.
Post through the built-in browser (owner logged in on laptop); typing fails when the pane is hidden → insert text with
document.execCommand('insertText') in the editor. Nothing about Vent Debout youngsters, ever.

## Mindveto site (BUILT 12 Nov) — repo sakkesakke/mindveto, live at mindveto.app (DNS set 12 Nov 15:40)
Astro static, 20 pages x 8 languages (EN/NL/FR/ES/DE/PT/IT/AR, Arabic RTL; 'made in Belgium' removed from marketing 12 Nov; apps still EN/NL/FR only — next: translate extension/app), Lighthouse 100/100/100/100, axe 0, self-hosted Atkinson Hyperlegible Next.
Pages source = GitHub Actions, custom domain mindveto.app; Namecheap DNS: 4 A @ 185.199.108-111.153 + CNAME www.
Downloads copied daily from human-override/ by sync-lists.yml. Rules for that repo: its own CLAUDE.md.
13 Nov: family page `family` = /block-porn/ (8 languages, footer + parents + home + llms.txt); quality gate in deploy.yml: `scripts/check.py` (links,
titles, hreflang) + `scripts/lighthouse.sh` (12 pages, every score >= 90; 13 Nov all 98-100). Android APK publish step was failing silently
since 10 Nov (pull --rebase with unstaged file): fixed #188, site now serves the build with the family filter (389 KB). AMO summary says 150+.
Open: Enforce HTTPS after cert. Done 12 Nov: hello@mindveto.app → owner Gmail (Namecheap), apps renamed to Mindveto 1.3.0.
SEO + security pass 12 Nov: sitemap hreflang/x-default + lastmod, VideoObject, IndexNow ping in deploy.yml (public key
file), actions pinned to SHAs, dependabot, /.well-known/security.txt; npm audit 0. Google Search Console verified 12 Nov (account geopolcoins1@,
file public/google28b43fb835ba26d8.html — never delete), sitemap-index.xml submitted OK. GEO 12 Nov: /llms.txt (built from EN content), guide page `guide` = /block-chatgpt/ (+NL/FR), WebPage + home SoftwareApplication schema. Bing Webmaster verified 12 Nov (meta msvalidate.01 on EN home in Base.astro — never remove), sitemap submitted.
DMARC added 12 Nov: TXT `_dmarc` = `v=DMARC1; p=quarantine; adkim=r; aspf=r` (before sending AS hello@: set up DKIM first).
17 Nov (1.6.1): NEW builds fetch lists from mindveto.app/downloads/ (extension LIST_URL, Android URL_LIST + privacy/site links,
PC scripts, pro README). Old geopolcoins.xyz/human-override/ files stay published forever (old installs). Still on geopolcoins.xyz:
REMOVED_URL (no mindveto 'removed' page yet), Android TERMS_URL, never-block entry. 17 Nov: mindveto.app offers 1.6.1 (mindveto#5,
sync-lists.yml names 1.6.1); 1.6.0 zip deleted from both repos.
18 Nov (1.7.0, NOT in stores; owner decides): night-mode button in the schedule card (every night 22:00-07:00) +
AI "undress"/fake-nude sites in the adult list (`adult/nudify.txt`, from CC0 aegis-blocklist ai-adult + clothoff.io; build_ho_lists merges it;
reaches extension, Android asset and PC hosts). Test `test/e2e/night_nudify.py`. Night mode is extension-only for now.
Council of 16 (18 Nov) picked: test page, honest bypass list, nudify blocker, night mode;
next by group: school starter pack (8.0), office "use our AI instead" redirect (7.5), shadow-AI count scan (7.3).
Round 3 best: parents "AI friend" heads-up in the popup (6.7), schools per-lesson AI switch (7.7) + 5-min AI-literacy course (7.0),
business Edge/Intune rollout file (7.0) + AI Act/GDPR proof report (6.8). Live 18 Nov on mindveto.app: /is-it-working/ (probes 8 AI
sites on click, CSP widened on that page only) and /bypass-tricks/, 8 languages. mindveto.app offers 1.8.0 since 18 Nov (mindveto#9; sync-lists.yml names the zip: bump it + rm the old zip on every version, else the daily sync 404s).
18 Nov: checked with GoogleChrome/modern-web-guidance (CLI `npx modern-web-guidance@1.0.0 legacy-scan dist` = 0; `search`/`retrieve` for guides). mindveto#12: <pre><code> region, Speculation Rules prerender (moderate, no downloads), @view-transition, font-size-adjust.
18 Nov blog (mindveto#13): /blog/ + 2 articles x 8 langs (charai = "Is Character.AI safe for kids?", aiact = "AI Act Article 4 for schools"); Page.article = byline + sources + Article schema. Next: 1 article/week (answer-first, sources, FAQ; check facts on the day); check Search Console > Prestaties after ~4 weeks.
Blog queue (owner OK 18 Nov, in this order): A1 ChatGPT + customer data/GDPR (offices, paste guard) · A2 Snapchat My AI: safe/turn off? (honest: in-app, Mindveto can't block it) · A3 AI nudify apps (family filter) · A4 Can teachers detect ChatGPT? (detectors unreliable, exam button) · A5 Block AI on school Chromebooks (Google Admin) · A6 Meta AI in WhatsApp/Instagram: can you turn it off? · A7 Shadow AI at work (offices, B3) · A8 AI companion apps parents should know (friend list).
Firefox AMO 1.6.1 SUBMITTED 17 Nov by owner (addons-linter 10.15.0: 0 errors, 1 expected warning); review pending.

## Human Override own site (plan 12 Nov)
NEW BRAND (owner 12 Nov): **Mindveto** — "the human override for AI". Owner bought **mindveto.app** (Namecheap).
TMview 12 Nov: no "Mindveto" mark (only unrelated "MindVet"). mindveto.com/.eu were free. Repo name: sakkesakke/mindveto.
Rename extension/app/store texts to Mindveto before the first store submission.
Plan doc: https://claude.ai/artifact/LNN3Fe2GHRQgCNqSuWCq8L (competition, prices, legal per region, sales test, design).
Domain: mindveto.app (bought). Old idea humanoverride.app dropped. New repo sakkesakke/mindveto,
Astro static, GitHub Pages, self-hosted fonts (Newsreader/Atkinson Hyperlegible/IBM Plex Mono), no cookies/trackers →
no banner, no geo-IP. Design "Kalme controle" (editorial + one real switch), NOT geopol style, no crypto.
Keep old list URLs on geopolcoins.xyz working forever (extension/Android/PC fetch them). Prices proposed: Free / Plus
€14,99/yr / School €1/pupil (min €149) / Business €2,50/user/mo. Play promo codes max 90 days → Founder (first 250,
1 yr free) via in-app counter. Before selling: KBO registration + business address (owner). German Impressum needs the business address too. UK mark "The Human Override"
filed 16 Mar 2026 (cl. 35/41) — trademark check before UK launch.

## YouTube @geopolcoins
Pipeline `tools/shorts/` (README). Task "YouTube Shorts wachtrij bijvullen" Wed + Sun 18:47 Brussels (owner PC on +
Claude desktop app). Upload in Studio with the built-in browser: set fields with `form_input` (keyboard typing
fails when the pane is hidden). Owner's own account @saidamghar7086 comments on the channel: never reply to those
(fake engagement). Pinning comments needs YouTube advanced-feature verification (owner).

## Site check 11 Nov
Full check done (audits, all 180 pages at 390 px, links, labels, workflows). Fixed: mobile overflow in blog posts +
kronos, 14 field labels, uptime check (was always red), link checker root dir, third-party actions pinned to SHAs.
Contact address on legal pages: hello@geopolcoins.xyz (owner must check it reaches his inbox).

## Decisions
- NotebookLM as "brain": no (no official API; unofficial tools need the owner's Google login).
- Open Generative AI (uncensored model hub): owner said do not use.
- Later (owner's choice, "niet nu"): own domain for Human Override (advice: humanoverride.app + .com, ~$26/yr;
  owner buys). Leave sakkemoto.com (old WordPress.com Business finance blog): export → merge best posts into
  geopolcoins blog + redirects, domain to Namecheap, cancel plan last. Founder test: blocking is free elsewhere;
  money is in business paste guard per seat (~€2-3/user/month) and schools.

## Ko-fi (12 Nov)
Pro Bot Blueprints live: ko-fi.com/s/2e4140cd37 ($39 PWYW; 21-page PDF + prompts + tools JSON, zip kept OUT of the
repo; build script was in the session scratchpad). pro-bots.html button points to it.

## Checked done (12 Nov)
Admin 2FA (verified factor, is_admin needs aal2). Brevo: key in Vault, brevo-sync cron, DOI templates EN/NL/FR,
3 automations "Starter Kit EN/NL/FR - 5 tips" Active. public.leads 0 sign-ups on 12 Nov (30 days: ~415 views, home 197).
Starter Kit CTAs added 12 Nov: home banner (src=home-banner, EN/NL/FR) + garage (src=garage). Measure leads by p_source.
X post with free.html?src=x posted by owner 12 Nov. Typefully API cannot publish X posts that contain a URL
(X policy): make the draft, owner clicks Publish.

## Token saving (12 Nov)
Cloud sessions: run `bash tools/graphify_session.sh` after the clone. 20 unused project skills removed (#160);
old skill `maiga-site-rules` disabled by owner.

## Reminders
12 Nov 12:00 hello@ forwarding (owner, Namecheap) · 12 Nov 19:00 launch sites · 12 Nov Public APIs · 14 Nov pricing ·
5 Jan 2027 Moroccan crypto law. YouTube task re-enabled 11 Nov (that day's run skipped: PC off). Owner to-do:
submit the extension to the stores. The Brain stays disabled.
