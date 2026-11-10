# Human Override — store kit (extension 1.0.9)

Upload file: `human-override/human-override-1.0.9.zip` (built by `python3 tools/build_ho_lists.py`).
Pictures: `docs/store-kit/screenshots/` (1280×800 screenshots + 440×280 promo tile). Icon: `human-override/extension/icons/128.png`.
Privacy policy URL: https://geopolcoins.xyz/privacy.html · Homepage: https://geopolcoins.xyz/human-override.html
Support: https://geopolcoins.xyz/human-override.html · Category: Productivity (Chrome/Edge), Privacy & Security (Firefox).
Developer accounts: Chrome $5 one-time, Edge free, Firefox free. The owner signs in and submits; never share passwords.

## Name and short description (max 132 chars)
- EN: Human Override: the AI kill switch — Block 150+ AI chatbots and AI tools with one switch. PIN lock, schedule, paste guard. Free.
- NL: Human Override: de AI-noodknop — Blokkeer 150+ AI-chatbots en AI-tools met één schakelaar. Pincode, schema, plakbewaker. Gratis.
- FR: Human Override : l’interrupteur anti-IA — Bloquez 150+ chatbots et outils d’IA d’un geste. PIN, horaire, garde-collage. Gratuit.

## Long description (EN; NL/FR: copy the matching texts from human-override.html)
Human Override is the AI kill switch for parents, schools, companies and anyone who wants to think for themselves.

• One big switch blocks 150+ AI chatbots, AI search, AI image/video/voice/music, AI writing & homework, AI coding and AI note-takers.
• PIN lock: nobody can turn it off or change the list without the PIN.
• Schedule: block only on school days 08:00-16:00, or every night.
• Paste guard (new): on AI sites, a warning before you paste a bank number, card number, ID number, a list of e-mail addresses, a secret key or text marked "confidential". Choose: don't paste, paste without the private parts, or paste anyway.
• Tamper log (new): see wrong PIN attempts, when it was switched off and when settings changed. A red "!" appears on the icon after a wrong PIN.
• Your own block and allow lists. The public block list updates once a day.

Private by design: no account, no tracking, no ads. Everything is checked on your device. Pasted text is never stored or sent.
Honest limits: it works in this browser only. Someone with full control of the computer can remove it (the browser then opens a page that says so). Schools and companies can force-install it with browser policy.
© 2026 Amghar Said. Free to use; see the terms of use.

## Single purpose (Chrome)
Help people keep AI services out of their browser: block AI websites and warn before private data is pasted into AI sites.

## Permission justifications
- declarativeNetRequest: block AI websites with the browser's own blocking rules (no traffic is read).
- storage: keep settings, PIN hash, block counter and tamper log on the device.
- alarms: refresh the public block list once a day and switch the schedule on/off.
- Host permission `<all_urls>`: needed so the blocking rules can redirect any AI address to the "blocked" page and also block AI copies served through translate.goog.
- Content script (AI sites only, listed in the manifest): the paste guard checks pasted text on AI chat, search, writing and coding sites. The check runs locally; nothing is sent.
- Remote code: No. The daily block list is data (domain names), not code.

## Data usage answers
Chrome "Privacy practices": collects no user data (tick none). Certify: not sold, not used for unrelated purposes, not used for credit.
Firefox: `data_collection_permissions: none` is already in the manifest.
Edge: same answers as Chrome.

## Test notes for reviewers
1. Click the toolbar icon: the big switch shows "AI BLOCKED". Open https://chatgpt.com: the Human Override page appears.
2. Tap the switch to "AI ALLOWED", open chatgpt.com and paste `IBAN BE71 0961 2345 6769`: the paste guard asks first.
3. Set PIN 1234, enter a wrong PIN and try a change: it is refused and the tamper log shows "Wrong PIN tried".
