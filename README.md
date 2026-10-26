# geopolcoins.xyz

Free AI tools that run in your browser. No account, nothing to install. English, Nederlands, Français.

**Live site: [geopolcoins.xyz](https://geopolcoins.xyz)**

| Tool | What it does |
|---|---|
| [Bot Garage](https://geopolcoins.xyz/garage.html) | Copy one of 24 free AI chatbots or build your own, then use it in ChatGPT, Claude, Discord, Telegram or X |
| [Pro bots](https://geopolcoins.xyz/pro-bots.html) | Blueprints for connected assistants: phone receptionist, inbox assistant, WhatsApp booking bot |
| [AI bots for salons](https://geopolcoins.xyz/ai-bots-salon.html), [real estate](https://geopolcoins.xyz/ai-bots-real-estate.html), [restaurants](https://geopolcoins.xyz/ai-bots-restaurant.html) | Ready-made assistants per trade, with one free bot to try |
| [AI bot Q&A](https://geopolcoins.xyz/answers.html) | 17 honest answers about AI chatbots for small businesses |
| [Free AI keys guide](https://geopolcoins.xyz/free-ai-api.html) | Free and cheap ways to run your own bot |
| [Meme Studio](https://geopolcoins.xyz/meme.html) | 190+ meme templates, pixel stickers and PNG download, made on your device |
| [Meme Factory](https://geopolcoins.xyz/factory.html) | One idea in, a complete meme launch kit out; works offline |
| [Chart School](https://geopolcoins.xyz/chart.html) | Learn to read candles, volume, RSI and pump-and-dumps on practice charts |
| [Mini-Chain](https://geopolcoins.xyz/chain.html) | Hash, mine and break a tiny blockchain yourself |
| [Bot Bank](https://geopolcoins.xyz/lend.html) | Lend play coins to AI bots and learn the risks of lending |
| [$MAIGA HQ](https://geopolcoins.xyz/hq.html) | Satirical meme coin info, Token Checkup, 8 arcade games, Launch Hub |

## How it is built

- Plain HTML, CSS and JavaScript on GitHub Pages. No build step, no framework, no ad trackers.
- Supabase (Postgres with row level security) for the small public parts: scores, counters and the quote form.
- Installable as an app (PWA) and partly usable offline.
- Every push is checked by Gitleaks (no secrets), CodeQL and a weekly link check.

## Files for maintainers

| Path | What it is |
|---|---|
| `index.html` | Start page with the tool picker (EN/NL/FR) |
| `hq.html` | $MAIGA HQ: coin info, arcade, swap, Launch Hub, terms |
| `admin.html` | Admin dashboard. Signs in with Supabase Auth and 2FA. Contains no secrets. |
| `supabase-*.sql` | Database setup and security, safe to re-run |
| `tools/` | Build scripts: offline zip, legal pages, Q&A page |
| `sw.js` | Service worker. Bump `VERSION` on each release. |

## Good to know

$MAIGA is a satirical meme coin. Entertainment only, not financial advice. The tools never ask for a seed phrase, private key or password.

Contact: geopolcoins1@gmail.com · [Privacy](https://geopolcoins.xyz/privacy.html) · [Legal](https://geopolcoins.xyz/legal.html)
