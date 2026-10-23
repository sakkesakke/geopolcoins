# Feature Specification: Installable $MAIGA web app

**Feature Branch**: `001-installable-web-app`
**Created**: 2026-10-23
**Status**: Draft
**Input**: User description: "Installable web app for geopolcoins.xyz users: install to home screen, an app home with the key tools as big tiles (Bot Garage, Token Checkup, Meme Factory, Battle of the day, My bots, Custom bot), a My bots list that works offline, offline support with honest notices, EN/NL/FR, no wallet access, no new tracking, new deploys must reach users."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install the app and open the tools fast (Priority: P1)

A visitor on their phone or computer sees an "Install the app" option, adds $MAIGA to their home screen, and from then on opens an app home with big tiles for the main tools.

**Why this priority**: This is the core of the feature: it turns one-time visitors into returning users with one tap.

**Independent Test**: Open the site on a supported phone or desktop browser, install it, launch it from the home screen and reach every tool from the app home.

**Acceptance Scenarios**:

1. **Given** a visitor on a browser that supports installing, **When** they press "Install the app", **Then** the browser's install prompt appears and, after accepting, an app icon with the $MAIGA pixel logo appears on their home screen.
2. **Given** a visitor on an iPhone or iPad (no install prompt), **When** they press "Install the app", **Then** they see short step-by-step instructions in their language for adding it to the home screen.
3. **Given** the app is installed, **When** the user opens it from the home screen, **Then** it opens in its own window on the app home with tiles for Bot Garage, Token Checkup, Meme Factory, Battle of the day, My bots and Custom bot.
4. **Given** the app is already installed or the browser cannot install apps, **When** the user visits the site, **Then** no broken or useless install button is shown.

---

### User Story 2 - My bots, always at hand (Priority: P2)

A user who built or copied a bot in the Bot Garage finds it under "My bots" in the app, can open it in the garage, copy its prompt, share its link or delete it, also without internet.

**Why this priority**: It gives a personal reason to come back and makes the garage feel like an app, not a one-off page.

**Independent Test**: Save a bot in the garage, open My bots (online and offline) and use each action.

**Acceptance Scenarios**:

1. **Given** the user saved bots in the garage on this device, **When** they open My bots, **Then** each bot shows its name, job and avatar colour.
2. **Given** a bot in the list, **When** the user chooses Open, Copy prompt, Share link or Delete, **Then** the bot opens in the garage, the prompt is copied, a share link is copied, or (after confirmation) the bot is removed.
3. **Given** no internet connection, **When** the user opens My bots, **Then** the list and the copy actions still work.
4. **Given** no saved bots, **When** the user opens My bots, **Then** they see a friendly empty state with a button to the Bot Garage.

---

### User Story 3 - Battle of the day on the app home (Priority: P3)

The app home shows today's Battle of the day match-up and the current votes, with a button to watch and vote in the garage.

**Why this priority**: A small daily reason to open the app; it reuses a feature that already exists.

**Independent Test**: Open the app home online and see today's match-up and vote counts; open it offline and see a clear "needs internet" notice instead.

**Acceptance Scenarios**:

1. **Given** the user is online, **When** the app home loads, **Then** it shows today's two bots and the vote counts.
2. **Given** the user is offline or the battle cannot load, **When** the app home loads, **Then** the tile says the battle needs internet, without errors.

---

### User Story 4 - Works when the connection drops, updates when it returns (Priority: P2)

A user with a bad connection can still open the app home, the garage and My bots. Live features clearly say they need internet. When a new version of the site is published, users get it without reinstalling.

**Why this priority**: Offline-friendly behaviour is what makes an installed app feel trustworthy; stale versions would break future updates.

**Independent Test**: Visit once online, go offline, reopen the app; publish a change and confirm it reaches the installed app on the next online visit.

**Acceptance Scenarios**:

1. **Given** the user visited the app once online, **When** they open it offline, **Then** the app home, the Bot Garage and My bots load, and a small notice says they are offline.
2. **Given** the user is offline, **When** they open the Token Checkup, the battle vote or other live data, **Then** they see a friendly message that this needs internet.
3. **Given** a new version of the site was published, **When** the user next opens the app online, **Then** they get the new version within that visit or the next one, without reinstalling or clearing anything.
4. **Given** the user is offline and opens a page that was never stored, **Then** they see a friendly offline page with a link back to the app home.

### Edge Cases

- The browser blocks storage (private mode): the app home still works; My bots shows that saving is not available in this mode.
- A saved bot has damaged data: it is skipped or shown as "cannot open", never breaking the list.
- The user's browser language is not EN, NL or FR: English is used.
- The app is opened inside another app's in-app browser that cannot install: the install button explains how to open the site in a normal browser.
- Very old browsers without offline support: the site keeps working as a normal website.
- Existing visitors who never install: nothing changes for them except an optional install button.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The site MUST be installable on browsers that support it, with the existing pixel logo as icon, the name "$MAIGA" and a standalone window.
- **FR-002**: The site MUST show an "Install the app" control only when installing is possible or when platform instructions (iOS, in-app browsers) are useful; it MUST be hidden once installed.
- **FR-003**: There MUST be an app home page that opens when the installed app starts, with large, accessible tiles for Bot Garage, Token Checkup, Meme Factory, Battle of the day, My bots and Custom bot.
- **FR-004**: The Custom bot tile MUST link to the service page in the user's language (EN, NL or FR).
- **FR-005**: All app labels MUST follow the browser language (EN, NL, FR), falling back to English.
- **FR-006**: My bots MUST list the bots saved on this device by the Bot Garage and offer Open, Copy prompt, Share link and Delete (with confirmation).
- **FR-007**: The app home, Bot Garage, My bots and an offline page MUST be available offline after one online visit.
- **FR-008**: Features that need live data (Token Checkup results, battle votes, trending coins, swap, community garage) MUST show a clear "needs internet" message when offline instead of failing silently.
- **FR-009**: Newly published versions of the site MUST reach installed users on their next online visit without manual steps; pages MUST never be served from an outdated store when the network is available.
- **FR-010**: The app MUST NOT access wallets, MUST NOT add new tracking, cookies or third-party analytics; it MAY count app-home visits with the existing anonymous counter.
- **FR-011**: The app MUST contain no price predictions, earnings claims or buy prompts, and keep the existing "Entertainment only. NFA. DYOR." notices.
- **FR-012**: The app home and My bots MUST meet the project's accessibility rules (skip link, landmarks, one main heading, labels, contrast, tap size) and work at phone width without horizontal scrolling.
- **FR-013**: Existing pages MUST keep working exactly as before for visitors who do not install the app.
- **FR-014**: Saved bots MUST stay only on the user's device; nothing about My bots is sent to the server.

### Key Entities

- **Saved bot**: a bot recipe the garage keeps on the user's device (name, job, category, skills, rules, look, language).
- **App home tile**: a shortcut with an icon, a label in three languages, a short description and a destination.
- **Stored page copy**: an offline copy of an app page, replaced automatically when a newer version is available.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A visitor can install the app and open the app home from the home screen in under 30 seconds on a supported phone.
- **SC-002**: After one online visit, the app home, Bot Garage and My bots open offline in under 2 seconds on a mid-range phone.
- **SC-003**: 100% of live features show a "needs internet" message when offline; zero blank screens or error pop-ups.
- **SC-004**: A newly published change is visible in an installed app on the first or second online launch after publishing, in 100% of test runs.
- **SC-005**: All existing site checks (site-check, security scans, accessibility audit) still pass with no new findings.
- **SC-006**: Within 4 weeks, app-home visits are measurable in the admin stats as a separate page, so the owner can see if the app is used.

## Assumptions

- "Saved bots" are the bots the Bot Garage already stores in the browser; if the garage currently keeps only the last bot, My bots will start with that bot and the garage will keep a small list (up to 20) from now on.
- Installing relies on the browser's own install feature; no app-store listing is part of this feature.
- The existing anonymous visit counter gets one new page label for the app home; no other analytics are added.
- Offline copies cover only the app's own pages and pixel images, not third-party sites (swap, Ko-fi, AI providers).
- The service page and garage already exist in EN/NL/FR or English; no new translations of the garage itself are in scope.
