-- Security audit 2026-11-10. Idempotent.
-- 1) Admin check: the email claim AND the fixed user id of the owner account (an email in a token is not enough on its own).
create or replace function public.is_admin()
returns boolean language sql stable set search_path to 'public' as $$
  select (select auth.uid()) = 'f22fd754-e06a-4fb3-b4e5-3c2342a4f383'::uuid
     and lower(coalesce(auth.jwt() ->> 'email','')) = lower('geopolcoins1@gmail.com')
     and coalesce(auth.jwt() -> 'app_metadata' ->> 'provider', '') = 'email'
$$;

-- 2) Spam brake for tables that visitors insert into directly (scores, wallets, tournament entries):
--    at most N new rows per minute and M per day for the whole table, so a script cannot fill the database.
create or replace function public.insert_brake()
returns trigger language plpgsql security definer set search_path to '' as $$
declare per_min int := TG_ARGV[0]::int; per_day int := TG_ARGV[1]::int; n int;
begin
  -- only visitors (anon / signed-in) are braked; the owner and the service role are not
  if coalesce(nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'role', '') not in ('anon', 'authenticated') then return new; end if;
  execute format('select count(*) from public.%I where created_at > now() - interval ''1 minute''', TG_TABLE_NAME) into n;
  if n >= per_min then raise exception 'too many new entries, try again in a minute' using errcode = 'P0001'; end if;
  execute format('select count(*) from public.%I where created_at > now() - interval ''1 day''', TG_TABLE_NAME) into n;
  if n >= per_day then raise exception 'daily limit reached, try again tomorrow' using errcode = 'P0001'; end if;
  return new;
end $$;
revoke all on function public.insert_brake() from public, anon, authenticated;

drop trigger if exists aa_brake on public.scores;
create trigger aa_brake before insert on public.scores for each row execute function public.insert_brake('30', '3000');
drop trigger if exists aa_brake on public.wallets;
create trigger aa_brake before insert on public.wallets for each row execute function public.insert_brake('10', '300');
drop trigger if exists aa_brake on public.tournament_entries;
create trigger aa_brake before insert on public.tournament_entries for each row execute function public.insert_brake('60', '5000');
