# Mindveto — store kit (extension 1.2.0)

Upload file: `human-override/human-override-1.3.0.zip` (built by `python3 tools/build_ho_lists.py`).
Pictures: `docs/store-kit/screenshots/` (1280×800 screenshots + 440×280 promo tile). Icon: `human-override/extension/icons/128.png`.
Privacy policy URL: https://geopolcoins.xyz/privacy.html · Homepage: https://mindveto.app/
Support: https://mindveto.app/ · Category: Productivity (Chrome/Edge), Privacy & Security (Firefox).
Developer accounts: Chrome $5 one-time, Edge free, Firefox free. The owner signs in and submits; never share passwords.

## Name and short description (max 132 chars)
- EN: Mindveto: the AI kill switch — Block 130+ AI chatbots and AI tools with one switch. PIN lock, schedule, paste guard. Free.
- NL: Mindveto: de AI-noodknop — Blokkeer 130+ AI-chatbots en AI-tools met één schakelaar. Pincode, schema, plakbewaker. Gratis.
- FR: Mindveto : l’interrupteur anti-IA — Bloquez 130+ chatbots et outils d’IA d’un geste. PIN, horaire, garde-collage. Gratuit.

## Long description (EN; NL/FR: copy the matching texts from human-override.html)
Mindveto is the AI kill switch for parents, schools, companies and anyone who wants to think for themselves.

• One big switch blocks 130+ AI chatbots, AI search, AI image/video/voice/music, AI writing & homework, AI coding and AI note-takers.
• PIN lock: nobody can turn it off or change the list without the PIN.
• Schedule: block only on school days 08:00-16:00, or every night.
• Paste guard: on AI sites, a warning before you paste a bank number, card number, ID number, a list of e-mail addresses, a secret key or text marked "confidential". Choose: don't paste, paste without the private parts, or paste anyway.
• Approved AI (new): tick the AI your school or company allows (ChatGPT, Copilot, Gemini, Claude, Mistral...). Everything else stays blocked and the paste guard keeps watching.
• Your own private words (new): add project names or customer numbers; the paste guard warns for those too.
• Exam button for teachers (new): a teacher makes a class at mindveto.app/exam-button/ and switches all AI off for the whole class during a test. No accounts, no pupil names.
• Tamper log: see wrong PIN attempts, when it was switched off and when settings changed. A red "!" appears on the icon after a wrong PIN.
• Your own block and allow lists. The public block list updates once a day.

Private by design: no account, no tracking, no ads. Nothing is sent to us, unless you choose to join a class for exam mode: then only the class code is sent, once a minute. Everything is checked on your device. Pasted text is never stored or sent.
Honest limits: it works in this browser only. Someone with full control of the computer can remove it (the browser then opens a page that says so). Schools and companies can force-install it with browser policy.
© 2026 Amghar Said. Free to use; see the terms of use.

## Single purpose (Chrome)
Help people keep AI services out of their browser: block AI websites and warn before private data is pasted into AI sites.

## Permission justifications
- declarativeNetRequest: block AI websites with the browser's own blocking rules (no traffic is read).
- storage: keep settings, PIN hash, block counter and tamper log on the device.
- alarms: refresh the public block list once a day and switch the schedule on/off.
- Host permission `<all_urls>`: needed so the blocking rules can redirect any AI address to the "blocked" page and also block AI copies served through translate.goog.
- Content script (AI sites and AI pages such as bing.com/chat and github.com/copilot, all listed in the manifest): the paste guard checks pasted text on AI chat, search, writing and coding sites. The check runs locally; nothing is sent.
- Network: daily block list from geopolcoins.xyz; optional exam mode asks zslzbfbqrtfpvgbjhssd.supabase.co (class code only).
- Remote code: No. The daily block list is data (domain names), not code.

## Data usage answers
Chrome "Privacy practices": collects no user data (tick none). Explain in the notes field: "Optional exam mode: if the user joins a class, the extension sends only the class code to our database once a minute to ask whether the teacher's exam is running. No personal data, no browsing data." Certify: not sold, not used for unrelated purposes, not used for credit.
Firefox: `data_collection_permissions: none` is already in the manifest.
Edge: same answers as Chrome.

## Test notes for reviewers
1. Click the toolbar icon: the big switch shows "AI BLOCKED". Open https://chatgpt.com: the Mindveto page appears.
2. Tap the switch to "AI ALLOWED", open chatgpt.com and paste `IBAN BE71 0961 2345 6769`: the paste guard asks first.
3. Set PIN 1234, enter a wrong PIN and try a change: it is refused and the tamper log shows "Wrong PIN tried".
