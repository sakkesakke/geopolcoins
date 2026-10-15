# $MAIGA Arcade

Static site (GitHub Pages) + Supabase for scores/tournament + Phantom for payouts.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole site: 9 playable games, Wheel, tournament, swap, **Launch Hub** (meme maker + team planner + Pump.fun), terms |
| `admin.html` | Payout dashboard. Signs in with a real Supabase account. Contains **no secrets**. |
| `play.html`, `play-flappy.html` | Standalone Flappy pages for X player cards |
| `supabase-security.sql` | Run once in Supabase to lock the database down |
| `CNAME` | Custom domain (`geopolcoins.xyz`) — leave as is |

## Deploy (GitHub Pages)

1. In your GitHub repo, upload/replace these files (Add file → Upload files). Delete `bloc2.txt` and `1bloc.txt` — they're already merged into `index.html`.
2. Settings → Pages → deploy from the `main` branch, root folder.
3. Wait ~1 minute and hard-refresh the site (Ctrl+Shift+R).

## Supabase lockdown (do this BEFORE the next tournament)

1. Supabase → **Authentication → Users → Add user**: create your admin account (email + a strong password you use nowhere else).
2. Same area: turn **off** "Allow new users to sign up".
3. Open `supabase-security.sql`, replace `YOUR_ADMIN_EMAIL` (3 places) with that email, paste into **SQL Editor** and run.
4. Open the function `start_today_tournament` and check it only creates a tournament when there isn't an active one.
5. Visit `/admin.html` and sign in with that email/password.

## Paying winners

1. Sign in on `/admin.html` → **Connect Phantom** (the wallet that holds the prize pool).
2. Check the three winners and wallets. If a name has more than one wallet attached, pick the right one.
3. **Send payouts** → approve each transaction in Phantom. Each payout is saved the moment it confirms; running it again skips winners who are already paid.
4. First time: test with tiny amounts (change `PRIZES` at the top of the script in `admin.html`) before sending the real prizes.
5. Optional but recommended: put a free Helius/QuickNode RPC URL in `RPC_URL` (the public one rate-limits).

## Things you must know

- **Scores can be faked.** Browser games send their own score. Review the top 3 before paying; real anti-cheat needs a server.
- **Wheel = points.** The wheel awards arcade points, shown as points and kept out of the tournament. The 24h limit lives in the browser, so it's a soft limit.
- **Launch Hub does not move money.** The team split is a planner. Pump.fun is a third party.
- **12 games are marked "coming soon"** (Plinko, Dunk, Slice, Breakout, 2048, Whack, Crossy, Bomber, Simon, Mines, Puzzle, Tower). They no longer give fake scores.
- Running a prize contest and swaps can be regulated depending on where you and your players live. The terms section is a starting point, not legal advice — ask a lawyer before real money flows at scale.
- X only shows player cards for approved domains, so the embed may not appear in tweets.
