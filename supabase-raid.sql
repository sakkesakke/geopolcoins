-- $MAIGA: MAIGA Raid leaderboard (raid.html). Free game, no prizes, no wallets.
-- Separate from public.scores on purpose: that table belongs to the old hq.html tournament.
-- Safe to run again.

create table if not exists public.raid_scores (
  id bigint generated always as identity primary key,
  handle text not null check (handle ~ '^[A-Za-z0-9_]{1,15}$'),
  hero text not null check (hero in ('jp','bolt')),
  score integer not null check (score between 0 and 30000),
  time_ms integer not null check (time_ms between 45000 and 7200000),
  coins integer not null default 0 check (coins between 0 and 500),
  deaths integer not null default 0 check (deaths between 0 and 999),
  lang text not null default 'en' check (lang in ('en','nl','fr')),
  hidden boolean not null default false,
  created_at timestamptz not null default now()
);
create index if not exists raid_scores_week on public.raid_scores (created_at desc, score desc);
create index if not exists raid_scores_score on public.raid_scores (score desc);
create table if not exists public.raid_brake (minute timestamptz primary key, n integer not null default 0);

alter table public.raid_scores enable row level security;
alter table public.raid_brake enable row level security;
revoke all on public.raid_scores from anon, authenticated;
revoke all on public.raid_brake from anon, authenticated;
-- admin can read and hide rows (admin.html / SQL editor)
grant select, update (hidden) on public.raid_scores to authenticated;
drop policy if exists rs_admin_read on public.raid_scores;
create policy rs_admin_read on public.raid_scores for select to authenticated using (public.is_admin());
drop policy if exists rs_admin_hide on public.raid_scores;
create policy rs_admin_hide on public.raid_scores for update to authenticated using (public.is_admin()) with check (public.is_admin());

-- Save a finished run. Returns {"rank": n} = place this week.
create or replace function public.raid_submit(p_handle text, p_hero text, p_score integer, p_time_ms integer,
                                              p_coins integer, p_deaths integer, p_lang text)
returns json language plpgsql security definer set search_path = public as $$
declare m timestamptz := date_trunc('minute', now()); c integer; wk timestamptz := date_trunc('week', now()); r integer;
begin
  if p_handle is null or p_handle !~ '^[A-Za-z0-9_]{1,15}$' then raise exception 'bad handle'; end if;
  if p_hero not in ('jp','bolt') then raise exception 'bad hero'; end if;
  if p_score is null or p_score < 0 or p_score > 30000 then raise exception 'bad score'; end if;
  if p_time_ms is null or p_time_ms < 45000 or p_time_ms > 7200000 then raise exception 'bad time'; end if;
  -- rough plausibility: you cannot score much faster than about 120 points per second of play
  if p_score > 1500 + (p_time_ms / 1000) * 120 then raise exception 'bad score'; end if;
  insert into public.raid_brake(minute, n) values (m, 0) on conflict (minute) do nothing;
  update public.raid_brake set n = n + 1 where minute = m returning n into c;
  delete from public.raid_brake where minute < now() - interval '1 hour';
  if c > 60 then raise exception 'busy'; end if;
  -- the same name can save at most 20 runs per day
  if (select count(*) from public.raid_scores where lower(handle) = lower(p_handle) and created_at > now() - interval '1 day') >= 20 then
    raise exception 'limit';
  end if;
  insert into public.raid_scores(handle, hero, score, time_ms, coins, deaths, lang)
    values (p_handle, p_hero, p_score, p_time_ms, greatest(0, least(coalesce(p_coins, 0), 500)),
            greatest(0, least(coalesce(p_deaths, 0), 999)), case when p_lang in ('en','nl','fr') then p_lang else 'en' end);
  select count(*) + 1 into r from (
    select lower(handle) h, max(score) s from public.raid_scores
     where created_at >= wk and hidden = false and lower(handle) <> lower(p_handle) group by lower(handle)) x
   where x.s > p_score;
  return json_build_object('rank', r);
end $$;
revoke all on function public.raid_submit(text, text, integer, integer, integer, integer, text) from public;
grant execute on function public.raid_submit(text, text, integer, integer, integer, integer, text) to anon, authenticated;

-- Top 20: best run per name, this week (Monday 00:00 UTC) or all time.
create or replace function public.raid_top(p_scope text) returns table(handle text, hero text, score integer, time_ms integer)
language sql stable security definer set search_path = public as $$
  select handle, hero, score, time_ms from (
    select distinct on (lower(handle)) handle, hero, score, time_ms, created_at
      from public.raid_scores
     where hidden = false and (p_scope = 'all' or created_at >= date_trunc('week', now()))
     order by lower(handle), score desc, time_ms asc) best
  order by score desc, time_ms asc
  limit 20;
$$;
revoke all on function public.raid_top(text) from public;
grant execute on function public.raid_top(text) to anon, authenticated;
