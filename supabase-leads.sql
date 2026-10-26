-- $MAIGA: Starter Kit sign-ups (free.html, EN/NL/FR).
-- Safe to run again. Visitors can only submit through submit_lead(); only the admin can read, update or delete.
-- Stored: email, optional first name, business type, language, where they signed up, and the exact consent text.

create table if not exists public.leads (
  id bigserial primary key,
  created_at timestamptz not null default now(),
  email text not null unique check (char_length(email) <= 120 and email ~* '^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'),
  name text not null default '' check (char_length(name) <= 40),
  btype text not null default 'other' check (btype in ('salon','realestate','horeca','shop','trades','health','other')),
  lang text not null check (lang in ('en','nl','fr')),
  source text not null default 'free' check (char_length(source) <= 40),
  consent text not null check (char_length(consent) between 10 and 300),
  status text not null default 'new' check (status in ('new','imported','unsubscribed'))
);
create table if not exists public.leads_brake (minute timestamptz primary key, n integer not null default 0);
alter table public.leads enable row level security;
alter table public.leads_brake enable row level security;
revoke all on public.leads from anon, authenticated;
revoke all on public.leads_brake from anon, authenticated;
grant select, update (status), delete on public.leads to authenticated;
drop policy if exists leads_admin on public.leads;
create policy leads_admin on public.leads for all to authenticated using ((select public.is_admin())) with check ((select public.is_admin()));
create index if not exists leads_created_idx on public.leads (created_at);

create or replace function public.submit_lead(p_email text, p_name text, p_type text, p_lang text, p_source text, p_consent text)
returns void language plpgsql security definer set search_path = public as $$
declare m timestamptz := date_trunc('minute', now()); c integer; e text := lower(trim(coalesce(p_email, '')));
begin
  insert into public.leads_brake(minute, n) values (m, 0) on conflict (minute) do nothing;
  update public.leads_brake set n = n + 1 where minute = m returning n into c;
  delete from public.leads_brake where minute < now() - interval '1 hour';
  if c > 20 then raise exception 'Too many sign-ups right now. Please try again in a few minutes.'; end if;
  if (select count(*) from public.leads where created_at > now() - interval '1 day') >= 300 then
    raise exception 'Too many sign-ups today. Please try again tomorrow.'; end if;
  if coalesce(p_name, '') ~* '(https?://|www\.|t\.me/|bit\.ly|<)' then
    raise exception 'Please use only your first name.'; end if;
  -- Same email again: keep the first sign-up, no error (no way to test which emails exist).
  insert into public.leads(email, name, btype, lang, source, consent)
  values (e, left(trim(coalesce(p_name, '')), 40), coalesce(nullif(p_type, ''), 'other'), p_lang, left(coalesce(nullif(p_source, ''), 'free'), 40), p_consent)
  on conflict (email) do nothing;
end $$;
revoke all on function public.submit_lead(text, text, text, text, text, text) from public;
grant execute on function public.submit_lead(text, text, text, text, text, text) to anon, authenticated;
