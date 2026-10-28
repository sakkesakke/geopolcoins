-- $MAIGA: "Log in with X" for the MAIGA Raid leaderboard. Safe to run again.
-- Requires supabase-raid.sql. X login stays OFF until: update public.raid_settings set x_login = true;

-- 1) Admin = the email/password account only. An X (or any other social) login can never be admin,
--    even if it would carry the same email address.
create or replace function public.is_admin() returns boolean
language sql stable set search_path = public as $$
  select lower(coalesce(auth.jwt() ->> 'email','')) = lower('geopolcoins1@gmail.com')
     and coalesce(auth.jwt() -> 'app_metadata' ->> 'provider', '') = 'email'
$$;

-- 2) On/off switch, read by the game.
create table if not exists public.raid_settings (id int primary key default 1 check (id = 1), x_login boolean not null default false);
insert into public.raid_settings(id) values (1) on conflict (id) do nothing;
alter table public.raid_settings enable row level security;
revoke all on public.raid_settings from anon, authenticated;
create or replace function public.raid_config() returns json
language sql stable security definer set search_path = public as $$
  select json_build_object('x_login', coalesce((select x_login from public.raid_settings where id = 1), false));
$$;
revoke all on function public.raid_config() from public;
grant execute on function public.raid_config() to anon, authenticated;

-- 3) Scores remember whether the name was checked by X.
alter table public.raid_scores add column if not exists verified boolean not null default false;
alter table public.raid_scores add column if not exists x_uid uuid;
create index if not exists raid_scores_xuid on public.raid_scores (x_uid, created_at desc);

-- 4) Typed names: only while X login is off.
create or replace function public.raid_submit(p_handle text, p_hero text, p_score integer, p_time_ms integer, p_coins integer, p_deaths integer, p_lang text)
returns json language plpgsql security definer set search_path = public as $$
declare m timestamptz := date_trunc('minute', now()); c integer; wk timestamptz := date_trunc('week', now()); r integer;
begin
  if coalesce((select x_login from public.raid_settings where id = 1), false) then raise exception 'login required'; end if;
  if p_handle is null or p_handle !~ '^[A-Za-z0-9_]{1,15}$' then raise exception 'bad handle'; end if;
  if p_hero not in ('jp','bolt') then raise exception 'bad hero'; end if;
  if p_score is null or p_score < 0 or p_score > 30000 then raise exception 'bad score'; end if;
  if p_time_ms is null or p_time_ms < 45000 or p_time_ms > 7200000 then raise exception 'bad time'; end if;
  if p_score > 1500 + (p_time_ms / 1000) * 120 then raise exception 'bad score'; end if;
  insert into public.raid_brake(minute, n) values (m, 0) on conflict (minute) do nothing;
  update public.raid_brake set n = n + 1 where minute = m returning n into c;
  delete from public.raid_brake where minute < now() - interval '1 hour';
  if c > 60 then raise exception 'busy'; end if;
  if (select count(*) from public.raid_scores where lower(handle) = lower(p_handle) and created_at > now() - interval '1 day') >= 20 then raise exception 'limit'; end if;
  insert into public.raid_scores(handle, hero, score, time_ms, coins, deaths, lang)
    values (p_handle, p_hero, p_score, p_time_ms, greatest(0, least(coalesce(p_coins, 0), 500)), greatest(0, least(coalesce(p_deaths, 0), 999)), case when p_lang in ('en','nl','fr') then p_lang else 'en' end);
  select count(*) + 1 into r from (select lower(handle) h, max(score) s from public.raid_scores where created_at >= wk and hidden = false and lower(handle) <> lower(p_handle) group by lower(handle)) x where x.s > p_score;
  return json_build_object('rank', r);
end $$;

-- 5) Save a score with the X username of the signed-in player (taken from the login, not from the browser).
create or replace function public.raid_submit_x(p_hero text, p_score integer, p_time_ms integer, p_coins integer, p_deaths integer, p_lang text)
returns json language plpgsql security definer set search_path = public as $$
declare m timestamptz := date_trunc('minute', now()); c integer; wk timestamptz := date_trunc('week', now()); r integer;
        uid uuid := auth.uid(); j jsonb := auth.jwt(); h text;
begin
  if uid is null then raise exception 'login required'; end if;
  if not coalesce((select x_login from public.raid_settings where id = 1), false) then raise exception 'x login off'; end if;
  if not (coalesce(j -> 'app_metadata' -> 'providers', '[]'::jsonb) ?| array['x','twitter']) then raise exception 'not an X login'; end if;
  h := coalesce(j -> 'user_metadata' ->> 'user_name', j -> 'user_metadata' ->> 'preferred_username');
  if h is null or h !~ '^[A-Za-z0-9_]{1,15}$' then raise exception 'no X username'; end if;
  if p_hero not in ('jp','bolt') then raise exception 'bad hero'; end if;
  if p_score is null or p_score < 0 or p_score > 30000 then raise exception 'bad score'; end if;
  if p_time_ms is null or p_time_ms < 45000 or p_time_ms > 7200000 then raise exception 'bad time'; end if;
  if p_score > 1500 + (p_time_ms / 1000) * 120 then raise exception 'bad score'; end if;
  insert into public.raid_brake(minute, n) values (m, 0) on conflict (minute) do nothing;
  update public.raid_brake set n = n + 1 where minute = m returning n into c;
  delete from public.raid_brake where minute < now() - interval '1 hour';
  if c > 60 then raise exception 'busy'; end if;
  if (select count(*) from public.raid_scores where x_uid = uid and created_at > now() - interval '1 day') >= 20 then raise exception 'limit'; end if;
  insert into public.raid_scores(handle, hero, score, time_ms, coins, deaths, lang, verified, x_uid)
    values (h, p_hero, p_score, p_time_ms, greatest(0, least(coalesce(p_coins, 0), 500)), greatest(0, least(coalesce(p_deaths, 0), 999)),
            case when p_lang in ('en','nl','fr') then p_lang else 'en' end, true, uid);
  select count(*) + 1 into r from (select lower(handle) hh, max(score) s from public.raid_scores
     where created_at >= wk and hidden = false and verified and lower(handle) <> lower(h) group by lower(handle)) x where x.s > p_score;
  return json_build_object('rank', r, 'handle', h);
end $$;
revoke all on function public.raid_submit_x(text, integer, integer, integer, integer, text) from public;
revoke execute on function public.raid_submit_x(text, integer, integer, integer, integer, text) from anon;
grant execute on function public.raid_submit_x(text, integer, integer, integer, integer, text) to authenticated;

-- 6) Leaderboard: adds the "verified" flag. With X login on, only checked names are shown.
drop function if exists public.raid_top(text);
create function public.raid_top(p_scope text) returns table(handle text, hero text, score integer, time_ms integer, verified boolean)
language sql stable security definer set search_path = public as $$
  select handle, hero, score, time_ms, verified from (
    select distinct on (lower(handle), verified) handle, hero, score, time_ms, verified, created_at from public.raid_scores
     where hidden = false and (p_scope = 'all' or created_at >= date_trunc('week', now()))
       and (verified or not coalesce((select x_login from public.raid_settings where id = 1), false))
     order by lower(handle), verified, score desc, time_ms asc) best
  order by score desc, time_ms asc limit 20;
$$;
revoke all on function public.raid_top(text) from public;
grant execute on function public.raid_top(text) to anon, authenticated;
