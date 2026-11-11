# Handoff (short) — state 11 Nov 2026

Loaded automatically through `CLAUDE.md`. Rules, owner and git/SQL workflow: `maiga-ops` skill.
Read other files only when the task needs them. Update this file after every larger task (keep it under ~50 lines).

## Release checklist
- `python3 tools/seo_enhance.py`, `tools/seo_audit.py`, `tools/security_audit.py` → 0 problems.
- Bump `VERSION` in `sw.js` (now `maiga-2026-11-10v`).
- Legal: `python3 tools/build_legal.py "" "" ""` (keep "[contact email]"), then `seo_enhance.py` again.
- Blog: `tools/blog_posts*.py` → `python3 tools/build_blog.py` (title ≤60, description 120-160).
- Extension changes: `python3 tools/build_ho_lists.py` (zip + content-script matches), then
  `git checkout` the 3 other HO zips (only timestamps change). Tests: `node --test human-override/test/detect.test.js`.

## Human Override (main product, © 2026 Amghar Said; birthplace never published)
Page `/human-override.html`, terms `/human-override-terms.html`. Code in `human-override/`:
extension 1.0.9 (`extension/`: paste guard, tamper log, PIN, schedule; lists in `extension/lists.json`),
Android (`android/`: tamper alerts, target SDK 36, CI builds APK + .aab), Windows `pc/HumanOverride.ps1`,
Mac/Linux `pc/human-override.sh`. Promo video live: https://youtu.be/c-_Isw8tUY8 (10 Nov).
Anonymous counter (site_views): `ho` = page visits; `ho_ext/ho_android/ho_win/ho_mac/ho_pro` = download clicks.

Open:
1. Pricing — reminder Sat 14 Nov 09:00 Brussels (proposal: Free / Plus €15/yr / Pro €180/yr / Custom).
2. Google Play — owner steps in `docs/google-play.md` (upload key → secrets HO_UPLOAD_*, $25, VPN declaration,
   12 testers × 14 days). Store kit for Chrome/Edge/Firefox in `docs/store-kit/`; owner submits.
3. Android camera/mic guard + tamper notification not yet tested on a real phone.
4. Next features: teacher exam button (needs backend), IT dashboard, AI Act/GDPR report, Human Override Box.
   Never: antivirus, own VPN, through-wall Wi-Fi surveillance.

## YouTube @geopolcoins
Pipeline `tools/shorts/` (README). Task "YouTube Shorts wachtrij bijvullen" Wed + Sun 18:47 Brussels (owner PC on +
Claude desktop app). Upload in Studio with the built-in browser: set fields with `form_input` (keyboard typing
fails when the pane is hidden). Owner's own account @saidamghar7086 comments on the channel: never reply to those
(fake engagement). Pinning comments needs YouTube advanced-feature verification (owner).

## Decisions
- NotebookLM as "brain": no (no official API; unofficial tools need the owner's Google login).
- Open Generative AI (uncensored model hub): owner said do not use.

## Reminders
12 Nov Public APIs · 14 Nov pricing · 5 Jan 2027 Moroccan crypto law. The Brain stays disabled.
