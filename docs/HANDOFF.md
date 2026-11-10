# Handoff: geopolcoins.xyz / Human Override (state on 10 Nov 2026)

Read this first in a new session, together with the `maiga-ops` skill (facts, trust rules, git + SQL workflow).

## The owner
- Belgian, lives in Morocco (Europe/Brussels or Africa/Casablanca). Beginner, writes mixed Dutch/English, often by voice.
- Answer in **simple Dutch**, numbered steps, exact button names. Wants everything **automatic** ("go" = build it all, report after).
- **Trust rules** (never break): no passwords or sign-ins for him; never change account security settings (give steps);
  API keys only by him in Supabase Vault or provider dashboards; no secrets anywhere; ask before public posts, spending
  money or anything irreversible; no automated likes/follows/replies; crypto: no price promises, always "Entertainment only.
  NFA. DYOR."; B2B outreach only to generic addresses after approval; check licenses and credit third-party code.
- Refused on purpose (do not build): through-wall Wi-Fi surveillance of people (e.g. RuView-style "see your kids").
  A *defensive* sensor check was built instead.

## Repo and workflow
- Repo `sakkesakke/geopolcoins` (GitHub Pages, branch `main`). Clone to `/home/claude/geopolcoins`.
- Branch → `git fetch origin main && git rebase origin/main` → push → PR via `gh api repos/sakkesakke/geopolcoins/pulls`
  → wait for check-runs (CodeQL, gitleaks, seo, build, Android build + emulator e2e when Android changes) → squash merge.
- Before every release: `python3 tools/seo_enhance.py`, `python3 tools/seo_audit.py` and `python3 tools/security_audit.py`
  must show 0 problems; bump `VERSION` in `sw.js` (now `maiga-2026-11-10t`).
- Legal pages: `python3 tools/build_legal.py "" "" ""` (the live pages keep the "[contact email]" placeholder; do not
  publish the owner's email unless he asks). Then run `seo_enhance.py` again.
- Blog: data in `tools/blog_posts*.py` (8 languages; a post may exist in fewer languages), `python3 tools/build_blog.py`.
  Descriptions 120-160 chars, titles ≤60.
- Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (+ the session line the system gives).

## Human Override ("the AI kill switch") — main product
Owner: © 2026 Amghar Said, all rights reserved (birthplace deliberately NOT published). Page: `/human-override.html`
(EN/NL/FR, live demo switch, device-aware download, four audiences, share funnel, thank-you dialog, FAQ schema,
links to 7 guides). Terms: `/human-override-terms.html`. Homepage has a banner + red nav link.

| Part | Where | State |
|---|---|---|
| Browser extension (MV3) **1.0.8** | `human-override/extension/`, zip `human-override/human-override-1.0.8.zip` | PIN (PBKDF2), categories incl. new **AI recorders & note-takers**, **schedule** (days + from/to, past midnight), translate.goog + Google AI Mode rules, welcome/terms. web-ext lint 0 errors. Store kit in scratchpad only (needs re-zipping with 1.0.8). |
| Android app | `human-override/android/` (Java, no AndroidX) | On-device DNS blocker (VpnService), PIN, daily list (bundled ∪ online), **sensor check** (ESP boards via Wi-Fi scan, `SensorCheck.java` + JVM tests), **camera & microphone guard** (`PrivacyGuard.java`, opt-in notification). CI builds a signed APK with a random key each time → `human-override/human-override-android.apk`. The guard notification is **not yet verified on a real phone** (emulator test could not find the switch). |
| Windows | `human-override/pc/HumanOverride.ps1` | Hosts-file blocker (1/2) + **option 3: switch off built-in AI** (20 official policies: Copilot, Recall, Click to Do, Paint AI, Edge Copilot/Compose, Chrome Gemini/AI Mode/Help me write…), **option 4 restores exact previous values** (backup in `HKLM\SOFTWARE\HumanOverride`). Tested with PowerShell 7 parser + mocked registry. |
| Mac/Linux | `human-override/pc/human-override.sh` | Hosts-file blocker. |
| Pro pack | built by `tools/build_ho_lists.py` | Chrome/Edge/Firefox policies, BIND RPZ, Unbound, dnsmasq, Windows DNS, Squid, firewall list. |
| Lists | `human-override/extension/lists.json` (source) → `tools/build_ho_lists.py` | 7 categories; PROTECT set of everyday domains never blocked. |
| Promo video | media branch: `human-override-promo.mp4` (16:9, 80 s) + `human-override-short.mp4` (9:16) | Voice = Kokoro bm_george, every line checked with faster-whisper (`tools/promo/voice_lines.py`, workflow `promo-voice.yml`). Render scripts are in the old session scratchpad only. |

### Human Override open items
1. **Pricing decision** (reminder scheduled Sat 14 Nov 09:00 Brussels): proposal = Free forever + Plus €15/yr (14-day
   trial) + Pro €180/yr + Custom. Needs a payment provider (Lemon Squeezy/Paddle), license keys, terms update. Not legal/tax advice.
2. **Google Play** (owner asked): $25 one-time, 15% per subscription, Google handles EU VAT; new personal accounts need
   **12 testers for 14 days**; needs a **stable signing key** stored by the owner as a GitHub secret; VPN-use declaration.
3. Next features on the agreed list: **teacher exam button** (one teacher switches AI off for a class; needs a small
   backend), **central dashboard for IT**, **paste guard** (warn when pasting IBAN/emails/"confidential" into AI sites),
   **tamper alerts**, monthly **AI Act / GDPR report**, a physical **Human Override Box** (Raspberry Pi + button).
   Do NOT build antivirus or our own VPN; a labelled VPN partner/affiliate is fine.
4. Store submissions (Firefox/Edge free, Chrome $5) are done by the owner with the store kit; update the kit to 1.0.8.

## Security (audit 10 Nov 2026, all fixed)
- Git history (405 commits, 129 branches) scanned with gitleaks: no real secrets (only public keys by design).
- Supabase `zslzbfbqrtfpvgbjhssd`: RLS on every table; `is_admin()` = owner user id `f22fd754-…` + email + email
  provider + **aal2 (2FA)** (`supabase-admin-mfa.sql`, emergency undo inside). Spam brake trigger `insert_brake()` on
  scores (30/min), wallets (10/min), tournament_entries (60/min) (`supabase-audit-2026-11.sql`).
- Owner did: 2FA on admin, **sign-ups disabled**. Old edge functions `geo` and `smart-task` return 410 (not deleted).
- Admin/crm/reset pages refuse to load in a frame. Leaked-password protection needs a paid Supabase plan.

## YouTube channel @geopolcoins (UCQcT-ameRR-Ew_79II0bbPA)
- 9 Nov: 10 videos, 1 subscriber, 379 views. Goal: monetization (YPP ≈ 1,000 subs + 4,000 watch h/12 mo or 10 M Shorts
  views/90 d — verify current rules). Biggest risk: "mass-produced/repetitive" content → variety matters.
- Pipeline `tools/shorts/` (README explains formats): default tips + new **"Scam or not?" quiz** (`"kind":"quiz"`),
  `no_extra`, `format: landscape`. Topics in `topics.json`; Human Override videos first in the queue; 3 quiz Shorts voiced.
- Scheduled task **"YouTube Shorts wachtrij bijvullen"** (Wed + Sun 18:47 Brussels) uploads via the built-in browser on the
  owner's computer (must be on, Claude desktop app open, Studio signed in). Last run on 8 Nov failed (usage limit).

## Marketing and SEO
- 7 Human Override guides in EN/NL/FR (kids, schools, company data, protect your home, launch article, turn off
  Copilot/Recall/Gemini, AI note-takers). IndexNow is pinged automatically by `seo-auto.yml` on every push (Bing etc.).
- Google Search Console: owner re-submitted `sitemap.xml` + `blog-feed.xml` on 10 Nov after "Impossible de lire le
  sitemap" (the files were verified valid and served with status 200 — likely the usual first-fetch delay).
- X @greenlandusa1 and Bluesky @geopolcoins.bsky.social (owner says Bluesky works again) via Typefully social set 348310
  (free plan, 10 posts/month). Owner posts the Human Override launch posts **manually**.
- Skills added to the repo: 7 `addy-*` engineering skills (MIT, credited, SkillSpector baselines in `.skillspector/`).
  OmniRoute was **not** installed (sends code to unknown providers).

## Other scheduled reminders
- 12 Nov: "Public APIs on GitHub" reminder. 14 Nov: Human Override pricing. 5 Jan 2027: Moroccan crypto law check.
- The Brain (AI chat) stays **disabled** for visitors (`srv.settings brain_enabled=false`, `guide.js BRAIN_ON=false`).
