<!--
Sync Impact Report
- Version change: template -> 1.0.0 (first ratified version)
- Principles added: I. Honesty first, II. No secrets and minimal data, III. Safety of visitors and wallets,
  IV. Reuse first (ponytail), V. Tested before live, VI. Accessible, light and trilingual
- Sections added: Legal and platform rules, Workflow, Governance
- Templates: plan/spec/tasks templates need no change (Constitution Check reads this file)
- Deferred: none
-->

# $MAIGA / geopolcoins.xyz Constitution

## Core Principles

### I. Honesty first (NON-NEGOTIABLE)
No price promises, earnings claims, buy pressure, fake scarcity, fake reviews, fake volume or fake engagement.
Every page about the coin says "Entertainment only. NFA. DYOR." Paid placements are always labelled
"Ad", "Partner" or "Sponsored". Products and services are described before anyone can pay, and prices are
agreed before work starts. Outreach is small, personal, and stops at the first "no".

### II. No secrets and minimal data (NON-NEGOTIABLE)
No API keys, service keys, webhooks, passwords, seed phrases or private RPC links in the site, the repo,
chats or posts. Only the Supabase publishable key may appear (public by design). Collect the minimum personal
data, say why on the page, and delete request data within 12 months. Gitleaks and CodeQL must pass before merge.

### III. Safety of visitors and wallets (NON-NEGOTIABLE)
Nothing on the site trades, auto-buys or touches a visitor's wallet; payouts are signed by the owner in Phantom.
Untrusted text (user input, API data, AI output) is rendered as text, never as HTML. Every public write goes
through a Supabase function with input checks and a rate-limit brake table; tables use row level security and
anonymous users get no direct table access. Bots never give medical, legal, tax or financial advice.

### IV. Reuse first (ponytail)
Before writing code, search the repo for something to reuse or extend (visit counter, garage helpers, pixel
characters, brake pattern, page generators). New libraries or CDN scripts only when a feature truly needs them.
Pages stay single, self-contained files (GitHub Pages, no build step); report the size change of every page.

### V. Tested before live
Every change is tested with Playwright against a local copy with external calls mocked: happy path, bad input,
XSS strings, phone width (no horizontal scroll), no JavaScript errors. Database changes are kept as idempotent SQL
files in the repo and verified with read queries and a rolled-back anonymous test before the site uses them.

### VI. Accessible, light and trilingual
Pages have a skip link, landmarks, one h1, correct heading order, labels, sufficient contrast and tap targets.
Titles and descriptions fit search results; business pages exist in English, Dutch and French with hreflang.
Original characters only (Jean-Phil pixel art, Cap'n Eagle, Bolt, Mevrouw Mintje, robots): no look-alikes of real people.

## Legal and platform rules
- Belgian gambling law: no paid-entry tournaments, bets or prizes for payment. Bot Battles have no stakes.
- X automation rules: no automated likes, follows, mass or keyword replies, or trend posting.
- Third-party terms: no tools that spoof clients or reuse consumer subscriptions outside their terms.
- Income is taxable: keep records; no tax advice is given.

## Workflow
- The owner is a Dutch-speaking beginner: explain in simple Dutch, numbered steps, exact button names.
- Work on a branch, open a PR via the REST API, wait for Gitleaks and CodeQL, then squash-merge.
- For bigger features use Spec Kit: /speckit-specify -> /speckit-plan -> /speckit-tasks -> /speckit-implement,
  and run the Constitution Check in the plan against these principles.
- Account and security settings, sign-ins and sending messages are done or approved by the owner.

## Governance
This constitution overrides other habits and templates in this repo. Amendments: edit this file in a PR,
explain the change in the Sync Impact Report, and bump the version (MAJOR for removing or redefining a
principle, MINOR for a new principle or section, PATCH for wording). Every plan must pass the Constitution
Check or document the justified exception.

**Version**: 1.0.0 | **Ratified**: 2026-10-23 | **Last Amended**: 2026-10-23
