-- ============================================================================
-- $MAIGA ARCADE — Supabase security setup
-- Run ONCE in: Supabase dashboard -> SQL Editor -> New query -> paste -> Run
--
-- BEFORE YOU RUN: replace YOUR_ADMIN_EMAIL (appears 3 times below) with the
-- email of the admin user you create in Supabase -> Authentication -> Users.
--
-- What this does
--   * players (anonymous) can only ADD scores / entries / wallets, with sane limits
--   * players can NOT read anyone's wallet address, change or delete anything
--   * only your admin account can read wallets, write payouts, or mark a tournament paid
--
-- It is wrapped in a transaction: if any line errors, NOTHING is changed.
-- ============================================================================
begin;

-- 1) Remove every old policy on these tables (old "allow all" policies would
--    silently defeat the new rules).
do $$
declare r record;
begin
  for r in
    select policyname, tablename from pg_policies
    where schemaname = 'public'
      and tablename in ('scores','tournament_entries','wallets','payouts','tournaments')
  loop
    execute format('drop policy %I on public.%I', r.policyname, r.tablename);
  end loop;
end $$;

-- 2) Turn Row Level Security on
alter table public.scores             enable row level security;
alter table public.tournament_entries enable row level security;
alter table public.wallets            enable row level security;
alter table public.payouts            enable row level security;
alter table public.tournaments        enable row level security;

-- 3) Table privileges: anonymous visitors get the minimum
revoke all on public.scores, public.tournament_entries, public.wallets, public.payouts, public.tournaments from anon;

grant select, insert on public.scores to anon;
grant insert         on public.wallets to anon;                 -- insert only: nobody can read wallets
grant select         on public.tournaments to anon;
grant select         on public.payouts to anon;                 -- payout history is public on-chain anyway
grant insert         on public.tournament_entries to anon;
-- leaderboard may read everything EXCEPT wallet_address:
grant select (tournament_id, pilot_name, score, game_type) on public.tournament_entries to anon;

-- your admin account (role "authenticated") needs full access, limited further by the policies below
grant select, insert, update on public.tournaments        to authenticated;
grant select, insert         on public.payouts            to authenticated;
grant select                 on public.tournament_entries to authenticated;
grant select                 on public.wallets            to authenticated;
grant select                 on public.scores             to authenticated;

-- 4) Policies ---------------------------------------------------------------

-- scores: anyone can read the leaderboard and add a score within limits
create policy scores_read on public.scores for select to anon, authenticated using (true);
create policy scores_add  on public.scores for insert to anon, authenticated
  with check (char_length(name) between 1 and 12 and score between 1 and 500000);

-- tournament entries: only into a currently ACTIVE tournament, only real games, sane values
create policy entries_read_anon on public.tournament_entries for select to anon, authenticated using (true);
create policy entries_add on public.tournament_entries for insert to anon, authenticated
  with check (
    char_length(pilot_name) between 1 and 12
    and score between 1 and 500000
    and game_type in ('invaders','runner','popper','snake','match','pacman','tetris','flappy')
    and (wallet_address is null or wallet_address ~ '^[1-9A-HJ-NP-Za-km-z]{32,44}$')
    and exists (select 1 from public.tournaments t where t.id = tournament_id and t.status = 'active')
  );

-- wallets: insert-only for players, readable only by the admin
create policy wallets_add on public.wallets for insert to anon, authenticated
  with check (char_length(name) between 1 and 12 and wallet ~ '^[1-9A-HJ-NP-Za-km-z]{32,44}$');
create policy wallets_admin_read on public.wallets for select to authenticated
  using ((auth.jwt() ->> 'email') = 'YOUR_ADMIN_EMAIL');

-- tournaments: everyone can see them, only the admin can change them (e.g. mark as paid)
create policy tournaments_read on public.tournaments for select to anon, authenticated using (true);
create policy tournaments_admin_update on public.tournaments for update to authenticated
  using ((auth.jwt() ->> 'email') = 'YOUR_ADMIN_EMAIL')
  with check ((auth.jwt() ->> 'email') = 'YOUR_ADMIN_EMAIL');

-- payouts: public read, only the admin can add
create policy payouts_read on public.payouts for select to anon, authenticated using (true);
create policy payouts_admin_add on public.payouts for insert to authenticated
  with check ((auth.jwt() ->> 'email') = 'YOUR_ADMIN_EMAIL');

-- 5) The site calls start_today_tournament() to create the daily tournament.
--    With the rules above, anonymous users can no longer insert into "tournaments"
--    directly, so that function must run with its owner's rights:
alter function public.start_today_tournament() security definer set search_path = public;
--    IMPORTANT: open that function once and check it only creates a tournament when
--    there is no active one for today. If it creates a new row on every call,
--    anyone could spam tournaments — fix the function before going live.

commit;

-- ============================================================================
-- Also do this in the dashboard (not SQL):
--   Authentication -> Sign In / Providers (or Settings): turn OFF "Allow new users to sign up".
--   Authentication -> Users -> Add user: create YOUR admin account (email + strong, unique password).
--
-- Honest limits: browser games can always be cheated by a determined person (the score is
-- sent by their browser). The limits above stop casual abuse (fake 99,999,999 scores, fake
-- games, wallet harvesting, tampering with payouts) but not scripted play. Real anti-cheat
-- needs a server (a Supabase Edge Function that validates runs). The admin page lets you
-- review the winners before paying.
-- ============================================================================
