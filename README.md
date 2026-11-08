# branch: server
Instructions for the free Oracle server of geopolcoins.xyz. The server pulls this branch every 5 minutes
(read-only, public URL, no token) and installs `server/crontab`. Nothing secret belongs here.

## Planned jobs (owner approved, 2026-11-07), build once the Oracle server runs
1. Live Rug Radar 24/7: scan new Solana pools continuously, aggregate red flags (facts, never name or rate one token on the site), feed radar.html + report/rugs pages.
2. Bolt AI: small open-source model on the server for free answers in 10 languages (no cost per question; education only).
3. Personal pixel Shorts: visitor enters a token address -> 20 s Jean-Phil Short with its public red flags, to download/share.
4. Daily news cartoon: daily pixel Short about crypto-safety news, 10 languages, posted to YouTube via the official API (owner creates the OAuth key himself).
5. Safety net: nightly Supabase backup to Oracle Object Storage + uptime alerts.
6. Live chat on the site and in the Pixel World (owner chose option 3): free text through a server filter that removes all links/domains, scam words and swearing (AI filter on this server), rate limit, plain-text rendering, report + mute; only the server may broadcast into the world channel. Update privacy pages.

## Running now
- `jobs/hello.sh` (every 10 min): checks in with the database. The server made its own random token
  (`/opt/maiga/secret/server-token`, chmod 600, never printed or committed); Supabase stores only its sha256
  and accepted the first registration only from this server's IP (51.170.140.207).
- `chat/` live chat filter (option 3): `chatd.py` pulls new visitor messages, removes links/domains/handles/
  addresses/phone numbers, blocks scam phrases and swearing, asks a local AI model (Ollama, MIT + Qwen2.5 1.5B,
  Apache-2.0) SAFE/BLOCK, then publishes or blocks. `run.sh` keeps it running; `ai-setup.sh` installs the model.
