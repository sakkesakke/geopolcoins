-- Weekly Language War champions (read-only, public). Applied 2026-11-07.
-- Also: track_view now accepts the pages badges, world and rugs.
create or replace function public.raid_champions(p_weeks int default 8)
returns table(week_start date, team text, points bigint, players integer)
language sql stable security definer set search_path to 'public' as $$
  with w as (
    select generate_series(date_trunc('week', now()) - make_interval(weeks => least(greatest(p_weeks,1),26)),
                           date_trunc('week', now()) - interval '1 week', interval '1 week') as ws
  ), best as (
    select w.ws, s.team, lower(s.handle) h, max(s.score) b
      from w join public.raid_scores s on s.created_at >= w.ws and s.created_at < w.ws + interval '1 week'
     where s.hidden = false and s.team is not null
       and (s.verified or not coalesce((select x_login from public.raid_settings where id = 1), false))
     group by w.ws, s.team, lower(s.handle)
  ), t as (
    select ws, team, sum(b)::bigint pts, count(*)::int pl, row_number() over (partition by ws order by sum(b) desc) rn
      from best group by ws, team
  )
  select ws::date, team, pts, pl from t where rn = 1 order by ws desc;
$$;
revoke all on function public.raid_champions(int) from public;
grant execute on function public.raid_champions(int) to anon, authenticated;
