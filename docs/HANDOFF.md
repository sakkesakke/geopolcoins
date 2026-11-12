# Handoff (short) — state 12 Nov 2026

Loaded automatically through `CLAUDE.md`. Rules, owner and git/SQL workflow: `maiga-ops` skill.
Read other files only when the task needs them. Update this file after every larger task (keep it under ~50 lines).
Code map: graphify (Apache-2.0, pinned 0.9.106) builds `graphify-out/` at session start (`tools/graphify_session.sh`,
local AST only, git-ignored). Use `graphify query|explain|path` before grep/read; `graphify update .` after edits.

## Release checklist
- `python3 tools/seo_enhance.py`, `tools/seo_audit.py`, `tools/security_audit.py` → 0 problems.
- Bump `VERSION` in `sw.js` (now `maiga-2026-11-12a`).
- Legal: `python3 tools/build_legal.py "" "" "hello@geopolcoins.xyz"` (owner OK 11 Nov; never his private
  address), then `seo_enhance.py` again.
- Blog: `tools/blog_posts*.py` → `python3 tools/build_blog.py` (title ≤60, description 120-160).
- Extension changes: `python3 tools/build_ho_lists.py` (zip + content-script matches), then
  `git checkout` the 3 other HO zips (only timestamps change). Tests: `node --test human-override/test/detect.test.js`.

## Human Override (main product, © 2026 Amghar Said; birthplace never published)
Page `/human-override.html`, terms `/human-override-terms.html`. Code in `human-override/`:
extension 1.2.1 (`extension/`: paste guard + own words, approved-AI picker (services in bundled lists.json only),
class + exam mode, tamper log, PIN, schedule + school holidays (skip/only, 8 regions BE/NL/FR, dates ONLY from the
bundled list: `python3 tools/build_ho_holidays.py <clone of openpotato/openholidaysapi.data>`, ODbL, refresh yearly;
BE German community has no data yet); lists in `extension/lists.json`),
Android (`android/`: tamper alerts, target SDK 36, CI builds APK + .aab), Windows `pc/HumanOverride.ps1`,
Mac/Linux `pc/human-override.sh`. Promo video live: https://youtu.be/c-_Isw8tUY8 (10 Nov).
Anonymous counter (site_views): `ho` = page visits; `ho_ext/ho_android/ho_win/ho_mac/ho_pro` = download clicks.

Open:
1. Pricing — reminder Sat 14 Nov 09:00 Brussels (proposal: Free / Plus €15/yr / Pro €180/yr / Custom).
2. Google Play — owner steps in `docs/google-play.md` (upload key → secrets HO_UPLOAD_*, $25, VPN declaration,
   12 testers × 14 days). Store kit for Chrome/Edge/Firefox in `docs/store-kit/`; owner submits.
3. Android camera/mic guard + tamper notification not yet tested on a real phone.
4. Teacher exam button is live (11 Nov): page `/human-override-class.html`, SQL `supabase-ho-exam.sql` (RPCs exam_create /
   exam_set / exam_status, table srv.ho_classes, only hashes; brake = 10 classes per device per hour via a hashed IP kept 1 h). Backend work goes on Supabase, not
   the Oracle server (no open ports). Browser tests: `python3 human-override/test/e2e/<name>.py` (shared setup in `common.py`; exam test needs
   `python3 -m http.server 8765` in the repo root).
   Next features: IT dashboard / central management, AI Act/GDPR report, Human Override Box.
   Never: antivirus, own VPN, through-wall Wi-Fi surveillance.

Free tool `/password-check.html` (12 Nov): Have I Been Pwned range API, k-anonymity, only 5 hash chars leave the browser.

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

## Token saving (12 Nov)
Cloud sessions: run `bash tools/graphify_session.sh` after the clone. 20 unused project skills removed (#160);
old skill `maiga-site-rules` disabled by owner.

## Reminders
12 Nov 12:00 hello@ forwarding (owner, Namecheap) · 12 Nov 19:00 launch sites · 12 Nov Public APIs · 14 Nov pricing ·
5 Jan 2027 Moroccan crypto law. YouTube task re-enabled 11 Nov (that day's run skipped: PC off). Owner to-do:
submit the extension to the stores. The Brain stays disabled.
