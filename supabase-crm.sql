-- $MAIGA CRM: contacts, pipeline and notes. Admin only. Safe to run again.
-- New quote requests (bot_requests) and Starter Kit sign-ups (leads) are added automatically.

create table if not exists public.crm_contacts (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  name text not null default '' check (char_length(name) <= 80),
  email text not null default '' check (char_length(email) <= 120),
  company text not null default '' check (char_length(company) <= 100),
  phone text not null default '' check (char_length(phone) <= 40),
  kind text not null default 'lead' check (kind in ('lead','customer','partner','supplier','other')),
  segment text not null default 'other' check (char_length(segment) <= 30),
  source text not null default 'manual' check (source in ('manual','bot_request','starter_kit','kofi','x','other')),
  source_id bigint,
  lang text not null default 'en' check (lang in ('en','nl','fr')),
  stage text not null default 'new' check (stage in ('new','contacted','quote','won','lost','nurture')),
  value_eur numeric(10,2) not null default 0 check (value_eur >= 0 and value_eur < 10000000),
  next_action text not null default '' check (char_length(next_action) <= 200),
  next_date date,
  tags text[] not null default '{}',
  first_message text not null default '' check (char_length(first_message) <= 1600),
  unique (source, source_id)
);
create index if not exists crm_contacts_stage on public.crm_contacts (stage, next_date);
create index if not exists crm_contacts_email on public.crm_contacts (lower(email));

create table if not exists public.crm_notes (
  id bigint generated always as identity primary key,
  contact_id bigint not null references public.crm_contacts(id) on delete cascade,
  created_at timestamptz not null default now(),
  kind text not null default 'note' check (kind in ('note','email','call','meeting','task','system')),
  body text not null check (char_length(body) between 1 and 4000)
);
create index if not exists crm_notes_contact on public.crm_notes (contact_id, created_at desc);

alter table public.crm_contacts enable row level security;
alter table public.crm_notes enable row level security;
revoke all on public.crm_contacts from anon, authenticated;
revoke all on public.crm_notes from anon, authenticated;
grant select, insert, update, delete on public.crm_contacts to authenticated;
grant select, insert, update, delete on public.crm_notes to authenticated;
drop policy if exists crm_c_admin on public.crm_contacts;
create policy crm_c_admin on public.crm_contacts for all to authenticated using (public.is_admin()) with check (public.is_admin());
drop policy if exists crm_n_admin on public.crm_notes;
create policy crm_n_admin on public.crm_notes for all to authenticated using (public.is_admin()) with check (public.is_admin());

create or replace function public.crm_touch() returns trigger language plpgsql set search_path = public as $$
begin new.updated_at := now(); return new; end $$;
drop trigger if exists crm_contacts_touch on public.crm_contacts;
create trigger crm_contacts_touch before update on public.crm_contacts for each row execute function public.crm_touch();

-- Automatic: a quote request becomes a CRM contact (stage "new") with a system note.
create or replace function public.crm_from_request() returns trigger
language plpgsql security definer set search_path = public as $$
declare cid bigint; seg text;
begin
  seg := case when new.message ilike '[robotics%' then 'robotics' else new.btype end;
  insert into public.crm_contacts(name, email, company, kind, segment, source, source_id, lang, stage, next_action, next_date, first_message)
  values (left(new.name, 80), left(new.email, 120), left(new.business, 100), 'lead', seg, 'bot_request', new.id, new.lang, 'new',
          'Reply with a first answer or a quote', (now() at time zone 'Europe/Brussels')::date + 1, left(coalesce(new.message, ''), 1600))
  on conflict (source, source_id) do nothing
  returning id into cid;
  if cid is not null then
    insert into public.crm_notes(contact_id, kind, body) values (cid, 'system', 'Quote request received via the website (' || seg || ').');
  end if;
  return new;
end $$;
drop trigger if exists bot_requests_to_crm on public.bot_requests;
create trigger bot_requests_to_crm after insert on public.bot_requests for each row execute function public.crm_from_request();

-- Automatic: a Starter Kit sign-up becomes a contact in stage "nurture" (they get the tip emails).
create or replace function public.crm_from_lead() returns trigger
language plpgsql security definer set search_path = public as $$
declare cid bigint;
begin
  insert into public.crm_contacts(name, email, kind, segment, source, source_id, lang, stage, first_message)
  values (left(coalesce(new.name, ''), 80), left(new.email, 120), 'lead', coalesce(new.btype, 'other'), 'starter_kit', new.id,
          case when new.lang in ('en','nl','fr') then new.lang else 'en' end, 'nurture', 'Starter Kit sign-up (' || coalesce(new.source, 'site') || ')')
  on conflict (source, source_id) do nothing
  returning id into cid;
  if cid is not null then
    insert into public.crm_notes(contact_id, kind, body) values (cid, 'system', 'Signed up for the free Starter Kit. Gets the 5 tip emails.');
  end if;
  return new;
end $$;
drop trigger if exists leads_to_crm on public.leads;
create trigger leads_to_crm after insert on public.leads for each row execute function public.crm_from_lead();

-- Unsubscribed in the leads table -> tag in the CRM.
create or replace function public.crm_lead_status() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.status = 'unsubscribed' and old.status is distinct from 'unsubscribed' then
    update public.crm_contacts set tags = array(select distinct unnest(tags || array['unsubscribed'])), stage = case when stage = 'nurture' then 'lost' else stage end
     where source = 'starter_kit' and source_id = new.id;
  end if;
  return new;
end $$;
drop trigger if exists leads_status_to_crm on public.leads;
create trigger leads_status_to_crm after update of status on public.leads for each row execute function public.crm_lead_status();

revoke all on function public.crm_from_request() from public, anon, authenticated;
revoke all on function public.crm_from_lead() from public, anon, authenticated;
revoke all on function public.crm_lead_status() from public, anon, authenticated;
revoke all on function public.crm_touch() from public, anon, authenticated;

-- Fill the CRM once with what already exists.
insert into public.crm_contacts(name, email, company, kind, segment, source, source_id, lang, stage, first_message, created_at)
select left(name, 80), left(email, 120), left(business, 100), 'lead',
       case when message ilike '[robotics%' then 'robotics' else btype end, 'bot_request', id, lang,
       case status when 'new' then 'new' when 'replied' then 'contacted' when 'done' then 'won' else 'lost' end,
       left(coalesce(message, ''), 1600), created_at
  from public.bot_requests where status <> 'spam'
on conflict (source, source_id) do nothing;
insert into public.crm_contacts(name, email, kind, segment, source, source_id, lang, stage, first_message, created_at)
select left(coalesce(name, ''), 80), left(email, 120), 'lead', coalesce(btype, 'other'), 'starter_kit', id,
       case when lang in ('en','nl','fr') then lang else 'en' end,
       case when status = 'unsubscribed' then 'lost' else 'nurture' end, 'Starter Kit sign-up', created_at
  from public.leads
on conflict (source, source_id) do nothing;

-- Privacy promise: leads that never became customers are removed after 12 months without activity.
create or replace function public.crm_cleanup() returns void
language sql security definer set search_path = public as $$
  delete from public.crm_contacts where stage <> 'won' and kind = 'lead' and updated_at < now() - interval '12 months';
$$;
revoke all on function public.crm_cleanup() from public, anon, authenticated;
do $$ begin
  if exists (select 1 from pg_extension where extname = 'pg_cron') then
    perform cron.unschedule(jobid) from cron.job where jobname = 'crm-cleanup';
    perform cron.schedule('crm-cleanup', '23 3 * * 1', 'select public.crm_cleanup()');
  end if;
end $$;
