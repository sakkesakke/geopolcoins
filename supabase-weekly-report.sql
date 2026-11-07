-- $MAIGA: weekly visitor report by email (Monday 07:00 Brussels time) + more page names for track_view.
-- Uses public.brevo_post() from supabase-brevo-sync.sql (Brevo key stays in Vault). Safe to run again.

-- 1) track_view: also count the newer pages separately
create or replace function public.track_view(p_page text, p_ref text)
returns void language plpgsql security definer set search_path = public as $$
declare m timestamptz := date_trunc('minute', now()); c integer; d date := (now() at time zone 'Europe/Brussels')::date; r text;
begin
  if p_page is null or p_page !~ '^(home|factory|garage|partners|play|ai|app|meme|chain|lend|raid|rug|radar|blog|widget|report|other)$' then return; end if;
  r := lower(coalesce(p_ref, 'direct'));
  if r !~ '^[a-z0-9.-]{1,60}$' then r := 'other'; end if;
  insert into public.views_brake(minute, n) values (m, 0) on conflict (minute) do nothing;
  update public.views_brake set n = n + 1 where minute = m returning n into c;
  delete from public.views_brake where minute < now() - interval '1 hour';
  if c > 3000 then return; end if;
  if r not in ('direct','internal') and (select count(distinct ref) from public.site_views where day = d) >= 150
     and not exists (select 1 from public.site_views where day = d and ref = r) then
    r := 'other';
  end if;
  insert into public.site_views(day, page, ref, n) values (d, p_page, r, 1)
    on conflict (day, page, ref) do update set n = public.site_views.n + 1;
end $$;
revoke all on function public.track_view(text, text) from public;
grant execute on function public.track_view(text, text) to anon, authenticated;

-- 2) the report (last 7 full days vs the 7 days before)
create or replace function public.weekly_report_html() returns table(subject text, html text)
language plpgsql stable security definer set search_path = public as $$
declare today date := (now() at time zone 'Europe/Brussels')::date; a date := today - 7; b date := today - 14;
  tot int; prev int; rows_pages text := ''; rows_refs text := ''; rows_teams text := ''; leads_n int; raid_n int; r record; pct text;
begin
  select coalesce(sum(n),0) into tot from site_views where day >= a and day < today;
  select coalesce(sum(n),0) into prev from site_views where day >= b and day < a;
  pct := case when prev = 0 then 'new' else to_char(round((tot - prev) * 100.0 / prev), 'FMS999') || '%' end;
  for r in select page, sum(n) filter (where day >= a) cur, sum(n) filter (where day < a) old
           from site_views where day >= b and day < today group by page order by 2 desc nulls last limit 15 loop
    rows_pages := rows_pages || format('<tr><td>%s</td><td align="right"><b>%s</b></td><td align="right" style="color:#888">%s</td></tr>', r.page, coalesce(r.cur,0), coalesce(r.old,0));
  end loop;
  for r in select ref, sum(n) cur from site_views where day >= a and day < today and ref not in ('direct','internal')
           group by ref order by 2 desc limit 10 loop
    rows_refs := rows_refs || format('<tr><td>%s</td><td align="right">%s</td></tr>', r.ref, r.cur);
  end loop;
  for r in select team, sum(best) pts, count(*) players from (
             select team, lower(handle) h, max(score) best from raid_scores
              where hidden = false and team is not null and created_at >= (a::timestamp at time zone 'Europe/Brussels') group by team, lower(handle)) x
           group by team order by 2 desc limit 10 loop
    rows_teams := rows_teams || format('<tr><td>%s</td><td align="right">%s pts</td><td align="right">%s players</td></tr>', r.team, r.pts, r.players);
  end loop;
  select count(*) into leads_n from leads where created_at >= (a::timestamp at time zone 'Europe/Brussels');
  select count(*) into raid_n from raid_scores where created_at >= (a::timestamp at time zone 'Europe/Brussels');
  subject := format('MAIGA weekly: %s visits (%s)', tot, pct);
  html := format($h$<div style="font-family:Arial,sans-serif;max-width:560px;color:#222">
<h2 style="margin:0 0 4px">geopolcoins.xyz this week</h2><p style="color:#666;margin:0 0 16px">%s to %s (Brussels time)</p>
<p style="font-size:28px;margin:0"><b>%s</b> page visits <span style="font-size:16px;color:#666">(week before: %s, %s)</span></p>
<p>New Starter Kit sign-ups: <b>%s</b> &middot; Raid scores saved: <b>%s</b></p>
<h3>Pages</h3><table width="100%%" cellpadding="4" style="border-collapse:collapse"><tr style="color:#888"><td>page</td><td align="right">this week</td><td align="right">week before</td></tr>%s</table>
<h3>Where visitors came from</h3><table width="100%%" cellpadding="4">%s</table>
<h3>Language war</h3><table width="100%%" cellpadding="4">%s</table>
<p style="color:#888;font-size:12px;margin-top:20px">Counts only, no personal data. Sent automatically every Monday by Supabase (job weekly-report). "other" = pages without their own name.</p></div>$h$,
    a, today - 1, tot, prev, pct, leads_n, raid_n, rows_pages,
    coalesce(nullif(rows_refs,''), '<tr><td>No outside links yet</td></tr>'),
    coalesce(nullif(rows_teams,''), '<tr><td>No team scores yet</td></tr>'));
  return next;
end $$;
revoke all on function public.weekly_report_html() from public, anon, authenticated;

create or replace function public.weekly_report_send() returns bigint
language plpgsql security definer set search_path = public as $$
declare s text; h text;
begin
  select subject, html into s, h from public.weekly_report_html();
  return public.brevo_post('/smtp/email', jsonb_build_object(
    'sender', jsonb_build_object('name', 'Bolt from geopolcoins.xyz', 'email', 'hello@geopolcoins.xyz'),
    'to', jsonb_build_array(jsonb_build_object('email', 'geopolcoins1@gmail.com')),
    'subject', s, 'htmlContent', h));
end $$;
revoke all on function public.weekly_report_send() from public, anon, authenticated;

-- 3) every Monday 06:00 UTC (07:00 Brussels in winter)
select cron.unschedule('weekly-report') where exists (select 1 from cron.job where jobname = 'weekly-report');
select cron.schedule('weekly-report', '0 6 * * 1', 'select public.weekly_report_send()');
