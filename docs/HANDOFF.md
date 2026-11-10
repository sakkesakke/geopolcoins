# Handoff (short) — state 10 Nov 2026

Read with the `maiga-ops` skill (owner, trust rules, git + SQL workflow). Read files only when the task needs them.

## Release checklist
- `python3 tools/seo_enhance.py`, `tools/seo_audit.py`, `tools/security_audit.py` → 0 problems.
- Bump `VERSION` in `sw.js` (now `maiga-2026-11-10v`).
- Legal: `python3 tools/build_legal.py "" "" ""` (keep "[contact email]"), then `seo_enhance.py` again.
- Blog: `tools/blog_posts*.py` → `python3 tools/build_blog.py` (title ≤60, description 120-160).

## Human Override (main product, © 2026 Amghar Said; birthplace never published)
Page `/human-override.html`, terms `/human-override-terms.html`. Code in `human-override/`:
extension 1.0.9 (`extension/`, lists in `extension/lists.json` → `tools/build_ho_lists.py`), Android (`android/`,
CI builds APK with random key), Windows `pc/HumanOverride.ps1` (option 3 = switch off built-in AI, 4 = restore),
Mac/Linux `pc/human-override.sh`. Promo videos on the media branch.

Open:
1. Pricing — reminder Sat 14 Nov 09:00 Brussels (proposal: Free / Plus €15/yr / Pro €180/yr / Custom).
2. Google Play — code ready (target SDK 36, .aab artifact, upload key from secrets HO_UPLOAD_*). Owner steps in
   `docs/google-play.md` (make key, 4 secrets, $25 account, VPN declaration + video, 12 testers × 14 days).
3. Store kit ready in `docs/store-kit/` (1.0.9); owner submits.
4. Android camera/mic guard notification not yet tested on a real phone.
5. Done 10 Nov: paste guard + tamper log (extension 1.0.9), tamper alerts (Android).
   Next features: teacher exam button (needs backend), IT dashboard,
   AI Act/GDPR report, Human Override Box. Never: antivirus, own VPN, through-wall Wi-Fi surveillance.

## YouTube @geopolcoins
Pipeline `tools/shorts/` (see its README). Task "YouTube Shorts wachtrij bijvullen" Wed + Sun 18:47 Brussels
(needs owner PC on + Claude desktop app). Last run 8 Nov failed (usage limit). Keep formats varied.

## Reminders
12 Nov Public APIs · 14 Nov pricing · 5 Jan 2027 Moroccan crypto law. The Brain stays disabled.
