# Implementation Plan: Installable $MAIGA web app

**Branch**: `001-installable-web-app` | **Date**: 2026-10-23 | **Spec**: [spec.md](./spec.md)

## Summary
Make geopolcoins.xyz installable (web app manifest + service worker), add an app home (`app.html`) with six tiles,
Battle of the day and My bots, an offline page, and a small shared `pwa.js` that registers the worker, shows the
install button / iOS steps and an offline notice. The garage gets a "Save to My bots" action that keeps up to 20
bots on the device.

## Technical Context
- **Language/Version**: plain HTML/CSS/JavaScript (ES2017), no build step; GitHub Pages hosting.
- **Primary Dependencies**: none new. Supabase RPC `battle_of_day` (existing) and `track_view` (existing; add page `app`).
- **Storage**: browser localStorage (`maiga_garage_bots_v1`, list of up to 20) and Cache Storage (service worker).
- **Testing**: Playwright (Chromium) against a local http.server with external calls mocked; offline via `context.set_offline`.
- **Target Platform**: modern mobile and desktop browsers; iOS Safari via "Add to Home Screen".
- **Performance Goals**: app home + My bots offline open in < 2 s; pwa.js < 4 KB; app.html < 25 KB.
- **Constraints**: pages stay self-contained; garage/factory CSP must allow `'self'` for scripts, workers and manifest.
- **Scale/Scope**: 1 new page, 1 offline page, 1 worker, 1 shared script, small edits to manifest, garage, index, factory, SQL.

## Constitution Check
| Principle | Status |
|---|---|
| I Honesty | Pass: no claims; tiles describe tools; disclaimers kept. |
| II No secrets / minimal data | Pass: only publishable key; My bots stays on device; no new tracking beyond `track_view('app')`. |
| III Safety | Pass: no wallet access; battle names rendered as text; worker never caches cross-origin or Supabase. |
| IV Reuse first | Pass: reuse pixel logo/icons, landing CSS tokens, garage share format, battle RPC, visit counter. One shared `pwa.js` instead of copies. |
| V Tested before live | Pass: Playwright tests for install UI, My bots actions, offline load, update path, mobile width, a11y audit. |
| VI Accessible, light, trilingual | Pass: EN/NL/FR labels, skip link, landmarks, tap targets. |

## Design decisions
- **Update safety (FR-009)**: HTML navigations are network-first (fresh page when online, cached copy only when offline);
  static same-origin files (icons, manifest, pwa.js) are stale-while-revalidate; worker uses a version string,
  `skipWaiting` + `clients.claim`, and deletes old caches. Cross-origin and Supabase requests are never cached.
- **Precache**: `/`, `app.html`, `garage.html`, `offline.html`, `pwa.js`, `site.webmanifest`, icons, logo.
- **Manifest**: `id` and `start_url` `/app.html?source=pwa`, `scope` `/`, `display` standalone, shortcuts to Garage, Checkup, My bots.
- **My bots data**: entries `{id, savedAt, bot, share, prompt}` written by the garage (it already builds share links and prompts),
  so the app only reads and copies. The current garage bot is also shown as "In your garage now".
- **Jekyll**: add `_config.yml` excluding `specs/` so spec files are not published.

## Project Structure
```
app.html          new: app home, battle tile, My bots
offline.html      new: offline fallback
pwa.js            new: worker registration, install button, iOS steps, offline banner, i18n
sw.js             new: service worker
site.webmanifest  updated: start_url, id, shortcuts
garage.html       updated: CSP, Save to My bots, nav link, pwa.js
factory.html      updated: CSP, pwa.js
index.html        updated: install button in footer, pwa.js
supabase-stats-battles.sql  updated: track_view allows 'app'
_config.yml       new: exclude specs
```
