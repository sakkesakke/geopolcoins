-- $MAIGA: "custom bot" requests from the service pages (EN/NL/FR).
-- Safe to run again. Visitors can only submit through submit_bot_request(); only the admin can read or update.

create table if not exists public.bot_requests (
  id bigserial primary key,
  created_at timestamptz not null default now(),
  lang text not null check (lang in ('en','nl','fr')),
  name text not null check (char_length(name) between 2 and 60),
  email text not null check (char_length(email) <= 120 and email ~* '^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'),
  business text not null check (char_length(business) between 2 and 80),
  btype text not null check (btype in ('salon','realestate','horeca','shop','trades','health','other')),
  message text not null default '' check (char_length(message) <= 1500),
  status text not null default 'new' check (status in ('new','replied','done','spam'))
);
create table if not exists public.requests_brake (minute timestamptz primary key, n integer not null default 0);
alter table public.bot_requests enable row level security;
alter table public.requests_brake enable row level security;
revoke all on public.bot_requests from anon, authenticated;
revoke all on public.requests_brake from anon, authenticated;
grant select, update (status), delete on public.bot_requests to authenticated;
drop policy if exists br_admin on public.bot_requests;
create policy br_admin on public.bot_requests for all to authenticated using (public.is_admin()) with check (public.is_admin());

create or replace function public.submit_bot_request(p_lang text, p_name text, p_email text, p_business text, p_type text, p_message text)
returns void language plpgsql security definer set search_path = public as $$
declare m timestamptz := date_trunc('minute', now()); c integer; e text := lower(trim(coalesce(p_email, '')));
begin
  insert into public.requests_brake(minute, n) values (m, 0) on conflict (minute) do nothing;
  update public.requests_brake set n = n + 1 where minute = m returning n into c;
  delete from public.requests_brake where minute < now() - interval '1 hour';
  if c > 10 then raise exception 'Too many requests right now. Please try again in a few minutes.'; end if;
  if (select count(*) from public.bot_requests where created_at > now() - interval '1 day') >= 100 then
    raise exception 'We received many requests today. Please try again tomorrow.'; end if;
  if (select count(*) from public.bot_requests where email = e and created_at > now() - interval '1 day') >= 3 then
    raise exception 'You already sent a request today. We will reply by email.'; end if;
  if coalesce(p_message, '') ~* '(https?://|www\.|t\.me/|bit\.ly)' then
    raise exception 'Please leave out links; describe your business in words.'; end if;
  insert into public.bot_requests(lang, name, email, business, btype, message)
  values (p_lang, trim(p_name), e, trim(p_business), p_type, trim(coalesce(p_message, '')));
end $$;
revoke all on function public.submit_bot_request(text, text, text, text, text, text) from public;
grant execute on function public.submit_bot_request(text, text, text, text, text, text) to anon, authenticated;
