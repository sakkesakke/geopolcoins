# Handoff (short) — state 12 Nov 2026

Loaded automatically through `CLAUDE.md`. Rules, owner and git/SQL workflow: `maiga-ops` skill.
Read other files only when the task needs them. Update this file after every larger task (keep it under ~50 lines).
Code map: graphify (Apache-2.0, pinned 0.9.106) builds `graphify-out/` at session start (`tools/graphify_session.sh`,
local AST only, git-ignored). Use `graphify query|explain|path` before grep/read; `graphify update .` after edits.

## Release checklist
- `python3 tools/seo_enhance.py`, `tools/seo_audit.py`, `tools/security_audit.py` → 0 problems.
- Bump `VERSION` in `sw.js` (now `maiga-2026-11-12d`).
- Legal: `python3 tools/build_legal.py "" "" "hello@geopolcoins.xyz"` (owner OK 11 Nov; never his private
  address), then `seo_enhance.py` again.
- Blog: `tools/blog_posts*.py` → `python3 tools/build_blog.py` (title ≤60, description 120-160).
- Extension changes: `python3 tools/build_ho_lists.py` (zip + content-script matches), then
  `git checkout` the 3 other HO zips (only timestamps change). Tests: `node --test human-override/test/detect.test.js`.

## Human Override (main product, © 2026 Amghar Said; birthplace never published)
Page `/human-override.html`, terms `/human-override-terms.html`. Code in `human-override/`:
extension 1.4.0 = **Mindveto** (renamed 12 Nov; hosts/registry markers still "Human Override" so old installs can be undone; Android package id unchanged; optional `social` category, OFF by default, extension-only, never in hosts/DNS lists, not forced by exam mode; test `test/e2e/social_media.py`) (`extension/`: paste guard + own words, approved-AI picker (services in bundled lists.json only),
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
   browser policies with backup), Mac/Linux (`family-on/off`). Test `test/e2e/family_filter.py`. Next: round 2 anti-bypass (VPN/proxy),
   round 3 gambling + dating (Plus).
   Next features: IT dashboard / central management, AI Act/GDPR report, Human Override Box.
   Never: antivirus, own VPN, through-wall Wi-Fi surveillance.

Free tool `/password-check.html` (12 Nov): Have I Been Pwned range API, k-anonymity, only 5 hash chars leave the browser.

## Mindveto site (BUILT 12 Nov) — repo sakkesakke/mindveto, live at mindveto.app (DNS set 12 Nov 15:40)
Astro static, 20 pages x 8 languages (EN/NL/FR/ES/DE/PT/IT/AR, Arabic RTL; 'made in Belgium' removed from marketing 12 Nov; apps still EN/NL/FR only — next: translate extension/app), Lighthouse 100/100/100/100, axe 0, self-hosted Atkinson Hyperlegible Next.
Pages source = GitHub Actions, custom domain mindveto.app; Namecheap DNS: 4 A @ 185.199.108-111.153 + CNAME www.
Downloads copied daily from human-override/ by sync-lists.yml. Rules for that repo: its own CLAUDE.md.
Open: Enforce HTTPS after cert. Done 12 Nov: hello@mindveto.app → owner Gmail (Namecheap), apps renamed to Mindveto 1.3.0.
SEO + security pass 12 Nov: sitemap hreflang/x-default + lastmod, VideoObject, IndexNow ping in deploy.yml (public key
file), actions pinned to SHAs, dependabot, /.well-known/security.txt; npm audit 0. Google Search Console verified 12 Nov (account geopolcoins1@,
file public/google28b43fb835ba26d8.html — never delete), sitemap-index.xml submitted OK. GEO 12 Nov: /llms.txt (built from EN content), guide page `guide` = /block-chatgpt/ (+NL/FR), WebPage + home SoftwareApplication schema. Bing Webmaster verified 12 Nov (meta msvalidate.01 on EN home in Base.astro — never remove), sitemap submitted.
DMARC added 12 Nov: TXT `_dmarc` = `v=DMARC1; p=quarantine; adkim=r; aspf=r` (before sending AS hello@: set up DKIM first).
Still on geopolcoins.xyz on purpose: extension LIST_URL + REMOVED_URL, PC hosts URL (old installs fetch them).

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
