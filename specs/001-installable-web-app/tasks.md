# Tasks: Installable $MAIGA web app

## Phase 1: Setup
- [x] T001 Add `_config.yml` excluding `specs/` from the published site
- [x] T002 Update `site.webmanifest` (id, start_url /app.html?source=pwa, scope, shortcuts)
- [ ] T003 Extend `track_view` to accept page `app` (SQL file done; migration waits for owner approval)

## Phase 2: Foundation
- [x] T004 Create `sw.js` (versioned caches, precache, network-first HTML, SWR static, never cross-origin)
- [x] T005 Create `offline.html` (EN/NL/FR, link to app home)
- [x] T006 Create `pwa.js` (register worker, install button for [data-install], iOS/in-app steps, offline banner, i18n)

## Phase 3: User Story 1 (P1) install + app home
- [x] T007 [US1] Create `app.html` with six tiles, language-aware Custom bot link, skip link, landmarks
- [x] T008 [US1] Add install control to `index.html` footer and `garage.html` nav; include pwa.js on index/garage/factory/app
- [x] T009 [US1] Allow `'self'` for script, worker and manifest in garage/factory CSP

## Phase 4: User Story 2 (P2) My bots
- [x] T010 [US2] Garage: "Save to My bots" button storing up to 20 entries {id, savedAt, bot, share, prompt}; nav link to My bots
- [x] T011 [US2] app.html My bots list with Open / Copy prompt / Share link / Delete (confirm), empty and no-storage states

## Phase 5: User Story 3 (P3) battle tile
- [x] T012 [US3] Battle tile on app.html via battle_of_day, text-only rendering, offline/error notice

## Phase 6: User Story 4 (P2) offline + updates
- [x] T013 [US4] "Needs internet" notices for live features when offline (garage community/battle, checkup tile)
- [x] T014 [US4] Test offline load and update path (new worker version replaces old cache)

## Phase 7: Polish
- [x] T015 Playwright tests: install UI, My bots actions, offline, mobile width, JS errors; accessibility audit
- [x] T016 Size check (ponytail), sitemap entry for app.html, PR, checks, merge
