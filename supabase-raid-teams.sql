-- $MAIGA: MAIGA Raid language teams ("Language war"). Free game, no prizes, no wallets.
-- A player picks a language team when saving a score. Each week the team totals are the sum of
-- every player's best run in that team. Nothing about the player's location is stored.
-- Needs supabase-raid.sql and supabase-raid-x.sql first. Safe to run again.

alter table public.raid_scores add column if not exists team text;
alter table public.raid_scores drop constraint if exists raid_scores_team_check;
alter table public.raid_scores add constraint raid_scores_team_check
  check (team is null or team in ('en','nl','fr','es','pt','de','tr','id','vi','ar'));
alter table public.raid_scores drop constraint if exists raid_scores_lang_check;
alter table public.raid_scores add constraint raid_scores_lang_check
  check (lang in ('en','nl','fr','es','pt','de','tr','id','vi','ar'));
create index if not exists raid_scores_team_week on public.raid_scores (created_at desc, team) where team is not null;

-- 1) Anonymous save: same checks as before, plus an optional team.
drop function if exists public.raid_submit(text, text, integer, integer, integer, integer, text);
create or replace function public.raid_submit(p_handle text, p_hero text, p_score integer, p_time_ms integer,
                                              p_coins integer, p_deaths integer, p_lang text, p_team text default null)
returns json language plpgsql security definer set search_path = public as $$
declare m timestamptz := date_trunc('minute', now()); c integer; wk timestamptz := date_trunc('week', now()); r integer;
        langs text[] := array['en','nl','fr','es','pt','de','tr','id','vi','ar'];
begin
  if p_handle is null or p_handle !~ '^[A-Za-z0-9_]{1,15}$' then raise exception 'bad handle'; end if;
  if p_hero not in ('jp','bolt') then raise exception 'bad hero'; end if;
  if p_score is null or p_score < 0 or p_score > 30000 then raise exception 'bad score'; end if;
  if p_time_ms is null or p_time_ms < 45000 or p_time_ms > 7200000 then raise exception 'bad time'; end if;
  if p_score > 1500 + (p_time_ms / 1000) * 120 then raise exception 'bad score'; end if;
  if p_team is not null and not (p_team = any(langs)) then raise exception 'bad team'; end if;
  insert into public.raid_brake(minute, n) values (m, 0) on conflict (minute) do nothing;
  update public.raid_brake set n = n + 1 where minute = m returning n into c;
  delete from public.raid_brake where minute < now() - interval '1 hour';
  if c > 60 then raise exception 'busy'; end if;
  if (select count(*) from public.raid_scores where lower(handle) = lower(p_handle) and created_at > now() - interval '1 day') >= 20 then
    raise exception 'limit';
  end if;
  insert into public.raid_scores(handle, hero, score, time_ms, coins, deaths, lang, team)
    values (p_handle, p_hero, p_score, p_time_ms, greatest(0, least(coalesce(p_coins, 0), 500)),
            greatest(0, least(coalesce(p_deaths, 0), 999)), case when p_lang = any(langs) then p_lang else 'en' end, p_team);
  select count(*) + 1 into r from (
    select lower(handle) h, max(score) s from public.raid_scores
     where created_at >= wk and hidden = false and lower(handle) <> lower(p_handle) group by lower(handle)) x
   where x.s > p_score;
  return json_build_object('rank', r);
end $$;
revoke all on function public.raid_submit(text, text, integer, integer, integer, integer, text, text) from public;
grant execute on function public.raid_submit(text, text, integer, integer, integer, integer, text, text) to anon, authenticated;

-- 2) Save with X login: same as supabase-raid-x.sql, plus an optional team.
drop function if exists public.raid_submit_x(text, integer, integer, integer, integer, text);
create or replace function public.raid_submit_x(p_hero text, p_score integer, p_time_ms integer, p_coins integer, p_deaths integer,
                                                p_lang text, p_team text default null)
returns json language plpgsql security definer set search_path = public as $$
declare m timestamptz := date_trunc('minute', now()); c integer; wk timestamptz := date_trunc('week', now()); r integer;
        uid uuid := auth.uid(); j jsonb := auth.jwt(); h text;
        langs text[] := array['en','nl','fr','es','pt','de','tr','id','vi','ar'];
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
  if p_team is not null and not (p_team = any(langs)) then raise exception 'bad team'; end if;
  insert into public.raid_brake(minute, n) values (m, 0) on conflict (minute) do nothing;
  update public.raid_brake set n = n + 1 where minute = m returning n into c;
  delete from public.raid_brake where minute < now() - interval '1 hour';
  if c > 60 then raise exception 'busy'; end if;
  if (select count(*) from public.raid_scores where x_uid = uid and created_at > now() - interval '1 day') >= 20 then raise exception 'limit'; end if;
  insert into public.raid_scores(handle, hero, score, time_ms, coins, deaths, lang, verified, x_uid, team)
    values (h, p_hero, p_score, p_time_ms, greatest(0, least(coalesce(p_coins, 0), 500)), greatest(0, least(coalesce(p_deaths, 0), 999)),
            case when p_lang = any(langs) then p_lang else 'en' end, true, uid, p_team);
  select count(*) + 1 into r from (select lower(handle) hh, max(score) s from public.raid_scores
     where created_at >= wk and hidden = false and verified and lower(handle) <> lower(h) group by lower(handle)) x where x.s > p_score;
  return json_build_object('rank', r, 'handle', h);
end $$;
revoke all on function public.raid_submit_x(text, integer, integer, integer, integer, text, text) from public;
revoke execute on function public.raid_submit_x(text, integer, integer, integer, integer, text, text) from anon;
grant execute on function public.raid_submit_x(text, integer, integer, integer, integer, text, text) to authenticated;

-- 3) This week's team table: best run per player per team, summed. Same visibility rule as raid_top.
create or replace function public.raid_teams() returns table(team text, points bigint, players integer)
language sql stable security definer set search_path = public as $$
  select team, sum(best)::bigint, count(*)::integer from (
    select team, lower(handle) h, max(score) best from public.raid_scores
     where hidden = false and team is not null and created_at >= date_trunc('week', now())
       and (verified or not coalesce((select x_login from public.raid_settings where id = 1), false))
     group by team, lower(handle)) x
  group by team order by 2 desc limit 10;
$$;
revoke all on function public.raid_teams() from public;
grant execute on function public.raid_teams() to anon, authenticated;
