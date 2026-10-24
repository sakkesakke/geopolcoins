-- $MAIGA: anonymous visitor stats + Bot Garage "Battle of the day".
-- Paste this whole file once in Supabase > SQL Editor > New query > Run.
-- Safe to run again. It only creates new things; it does not change or delete existing data.
-- Requires supabase-garage.sql (garage_bots) to have been run first.

------------------------------------------------------------------
-- 1) Anonymous page-view counter: page + day + referring website.
--    No cookies, no IP addresses, no user agents, no personal data.
------------------------------------------------------------------
create table if not exists public.site_views (
  day date not null,
  page text not null,
  ref text not null,
  n integer not null default 0,
  primary key (day, page, ref)
);
create table if not exists public.views_brake (minute timestamptz primary key, n integer not null default 0);
alter table public.site_views enable row level security;
alter table public.views_brake enable row level security;
revoke all on public.site_views from anon, authenticated;
revoke all on public.views_brake from anon, authenticated;
grant select on public.site_views to authenticated;
drop policy if exists sv_admin_read on public.site_views;
create policy sv_admin_read on public.site_views for select to authenticated using (public.is_admin());

create or replace function public.track_view(p_page text, p_ref text) returns void
language plpgsql security definer set search_path = public as $$
declare m timestamptz := date_trunc('minute', now()); c integer; d date := (now() at time zone 'Europe/Brussels')::date; r text;
begin
  if p_page is null or p_page !~ '^(home|factory|garage|partners|play|ai|app|meme|chain|lend|other)$' then return; end if;
  r := lower(coalesce(p_ref, 'direct'));
  if r !~ '^[a-z0-9.-]{1,60}$' then r := 'other'; end if;
  insert into public.views_brake(minute, n) values (m, 0) on conflict (minute) do nothing;
  update public.views_brake set n = n + 1 where minute = m returning n into c;
  delete from public.views_brake where minute < now() - interval '1 hour';
  if c > 3000 then return; end if;                                  -- flood: stop counting this minute
  if r not in ('direct','internal') and (select count(distinct ref) from public.site_views where day = d) >= 150
     and not exists (select 1 from public.site_views where day = d and ref = r) then
    r := 'other';                                                     -- keep the table small
  end if;
  insert into public.site_views(day, page, ref, n) values (d, p_page, r, 1)
    on conflict (day, page, ref) do update set n = public.site_views.n + 1;
end $$;
revoke all on function public.track_view(text, text) from public;
grant execute on function public.track_view(text, text) to anon, authenticated;

------------------------------------------------------------------
-- 2) Battle of the day: one fixed match-up per day, everyone votes.
------------------------------------------------------------------
create table if not exists public.battle_days (
  day date primary key,
  a_kind text not null check (a_kind in ('bot','tpl')),
  a_ref text not null,
  b_kind text not null check (b_kind in ('bot','tpl')),
  b_ref text not null,
  va integer not null default 0,
  vb integer not null default 0
);
create table if not exists public.battle_brake (minute timestamptz primary key, n integer not null default 0);
alter table public.battle_days enable row level security;
alter table public.battle_brake enable row level security;
revoke all on public.battle_days from anon, authenticated;
revoke all on public.battle_brake from anon, authenticated;
grant select on public.battle_days to anon, authenticated;
drop policy if exists bd_read on public.battle_days;
create policy bd_read on public.battle_days for select to anon, authenticated using (true);

-- Creates today's match-up on the first call (two random bots from the 10 most-liked community bots,
-- or two ready-made bots while the community garage is small) and returns it with the votes.
create or replace function public.battle_of_day() returns json
language plpgsql security definer set search_path = public as $$
declare d date := (now() at time zone 'Europe/Brussels')::date; ids bigint[]; tpls text[] := array['rugradar','memewriter','scamshield','cryptotutor','launchcoach','commmod','inbox','faqdesk','leadscout','invoicepal','reviewer','hookhunter','contentweek','roaster','mealbot','habit','studybuddy','newsdigest','whalewatch','meetingnotes','socialdesk','newsletter','tripplanner','budgetbuddy']; t text[]; bd public.battle_days; res json;
begin
  if not exists (select 1 from public.battle_days where day = d) then
    select array_agg(id) into ids from (select id from (select id from public.garage_bots where hidden = false order by likes desc, created_at desc limit 10) t10 order by random() limit 2) x;
    if ids is not null and array_length(ids, 1) = 2 then
      insert into public.battle_days(day, a_kind, a_ref, b_kind, b_ref) values (d, 'bot', ids[1]::text, 'bot', ids[2]::text) on conflict (day) do nothing;
    else
      select array_agg(v) into t from (select v from unnest(tpls) v order by random() limit 2) y;
      insert into public.battle_days(day, a_kind, a_ref, b_kind, b_ref) values (d, 'tpl', t[1], 'tpl', t[2]) on conflict (day) do nothing;
    end if;
  end if;
  select * into bd from public.battle_days where day = d;
  select json_build_object(
    'day', bd.day, 'va', bd.va, 'vb', bd.vb,
    'a', case when bd.a_kind = 'bot' then (select json_build_object('kind','bot','id',g.id,'name',g.name,'role',g.role,'cat',g.cat,'recipe',g.recipe,'nickname',g.nickname) from public.garage_bots g where g.id = bd.a_ref::bigint and g.hidden = false) else json_build_object('kind','tpl','id',bd.a_ref) end,
    'b', case when bd.b_kind = 'bot' then (select json_build_object('kind','bot','id',g.id,'name',g.name,'role',g.role,'cat',g.cat,'recipe',g.recipe,'nickname',g.nickname) from public.garage_bots g where g.id = bd.b_ref::bigint and g.hidden = false) else json_build_object('kind','tpl','id',bd.b_ref) end
  ) into res;
  return res;
end $$;
revoke all on function public.battle_of_day() from public;
grant execute on function public.battle_of_day() to anon, authenticated;

create or replace function public.battle_vote(p_side text) returns json
language plpgsql security definer set search_path = public as $$
declare d date := (now() at time zone 'Europe/Brussels')::date; m timestamptz := date_trunc('minute', now()); c integer; bd public.battle_days;
begin
  if p_side not in ('a','b') then raise exception 'bad side'; end if;
  insert into public.battle_brake(minute, n) values (m, 0) on conflict (minute) do nothing;
  update public.battle_brake set n = n + 1 where minute = m returning n into c;
  delete from public.battle_brake where minute < now() - interval '1 hour';
  if c > 300 then raise exception 'Too many votes right now. Try again in a minute.'; end if;
  if p_side = 'a' then update public.battle_days set va = va + 1 where day = d and va < 10000000;
  else update public.battle_days set vb = vb + 1 where day = d and vb < 10000000; end if;
  select * into bd from public.battle_days where day = d;
  return json_build_object('va', bd.va, 'vb', bd.vb);
end $$;
revoke all on function public.battle_vote(text) from public;
grant execute on function public.battle_vote(text) to anon, authenticated;
