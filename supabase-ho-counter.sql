-- Human Override: anonymous counters (10 Nov 2026). Same track_view as before, plus these "pages":
--   ho = visit of /human-override.html ; ho_ext / ho_android / ho_win / ho_mac / ho_pro = click on a download button.
-- Only day + page + referrer domain + count are stored (no IP, no cookies, no personal data). Idempotent.
CREATE OR REPLACE FUNCTION public.track_view(p_page text, p_ref text)
 RETURNS void
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
declare m timestamptz := date_trunc('minute', now()); c integer; d date := (now() at time zone 'Europe/Brussels')::date; r text;
begin
  if p_page is null or p_page !~ '^(home|factory|garage|partners|play|ai|app|meme|chain|lend|raid|rug|radar|blog|widget|report|badges|world|rugs|other|ho|ho_ext|ho_android|ho_win|ho_mac|ho_pro)$' then return; end if;
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
end $function$;
