-- YouTube channel numbers for the weekly e-mail (NOT YET APPLIED, waiting for owner approval).
-- Needs a free YouTube Data API key in the Supabase Vault named 'youtube_api_key', entered by the owner.
-- Without a key nothing is fetched and the e-mail simply skips the YouTube section.
create table if not exists public.yt_stats (day date primary key, subscribers integer, views bigint, videos integer);
alter table public.yt_stats enable row level security;
create table if not exists public.yt_pending (rid bigint primary key, made timestamptz default now());
alter table public.yt_pending enable row level security;
revoke all on public.yt_stats, public.yt_pending from anon, authenticated;

create or replace function public.yt_request() returns bigint
language plpgsql security definer set search_path to 'public','extensions','vault' as $$
declare k text; rid bigint;
begin
  select decrypted_secret into k from vault.decrypted_secrets where name = 'youtube_api_key' limit 1;
  if k is null then return null; end if;
  select net.http_get(url := 'https://www.googleapis.com/youtube/v3/channels?part=statistics&id=UCQcT-ameRR-Ew_79II0bbPA&key=' || k,
                      timeout_milliseconds := 10000) into rid;
  insert into public.yt_pending(rid) values (rid) on conflict do nothing;
  return rid;
end $$;

create or replace function public.yt_store() returns integer
language plpgsql security definer set search_path to 'public','extensions' as $$
declare r record; j jsonb; n int := 0;
begin
  for r in select p.rid, h.status_code, h.content from public.yt_pending p join net._http_response h on h.id = p.rid loop
    if r.status_code = 200 then
      j := (r.content::jsonb)->'items'->0->'statistics';
      if j is not null then
        insert into public.yt_stats(day, subscribers, views, videos)
        values ((now() at time zone 'Europe/Brussels')::date, (j->>'subscriberCount')::int, (j->>'viewCount')::bigint, (j->>'videoCount')::int)
        on conflict (day) do update set subscribers = excluded.subscribers, views = excluded.views, videos = excluded.videos;
        n := n + 1;
      end if;
    end if;
    delete from public.yt_pending where rid = r.rid;
  end loop;
  delete from public.yt_pending where made < now() - interval '1 day';
  return n;
end $$;
revoke all on function public.yt_request(), public.yt_store() from public, anon, authenticated;

select cron.schedule('yt-request', '30 5 * * 1', 'select public.yt_request()');
select cron.schedule('yt-store', '45 5 * * 1', 'select public.yt_store()');
-- + weekly_report_html(): adds "<h3>YouTube @geopolcoins</h3> subscribers (+diff) · views (+diff) · videos" when yt_stats has rows.
