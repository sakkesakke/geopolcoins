-- $MAIGA: automatic sync of Starter Kit sign-ups to Brevo (double opt-in).
-- Safe to run again. Needs a Vault secret named 'brevo_api_key' (added by the owner in the Supabase dashboard, never in code).
-- Flow: new row in public.leads -> Brevo sends the confirmation email -> on confirm Brevo adds the contact to the language list
-- -> the Brevo automation for that list sends the 5 tip emails.

alter table public.leads add column if not exists brevo_req bigint;
alter table public.leads add column if not exists synced_at timestamptz;
alter table public.leads drop constraint if exists leads_status_check;
alter table public.leads add constraint leads_status_check check (status in ('new','imported','unsubscribed','error'));

-- Per language: Brevo list id and double opt-in template id. Only the admin can read or change it.
create table if not exists public.brevo_config (
  lang text primary key check (lang in ('en','nl','fr')),
  list_id integer not null,
  doi_template_id integer,
  redirect_url text not null default 'https://geopolcoins.xyz/free.html?confirmed=1'
);
alter table public.brevo_config enable row level security;
revoke all on public.brevo_config from anon, authenticated;
grant select, update on public.brevo_config to authenticated;
drop policy if exists brevo_config_admin on public.brevo_config;
create policy brevo_config_admin on public.brevo_config for all to authenticated using ((select public.is_admin())) with check ((select public.is_admin()));
insert into public.brevo_config(lang, list_id) values ('en', 3), ('nl', 4), ('fr', 5) on conflict (lang) do nothing;

-- Generic Brevo API call (async via pg_net). Not callable by visitors.
create or replace function public.brevo_post(p_path text, p_body jsonb)
returns bigint language plpgsql security definer set search_path = public, extensions, vault as $$
declare k text; rid bigint;
begin
  select decrypted_secret into k from vault.decrypted_secrets where name = 'brevo_api_key' limit 1;
  if k is null then return null; end if;
  select net.http_post(
    url := 'https://api.brevo.com/v3' || p_path,
    body := p_body,
    headers := jsonb_build_object('api-key', k, 'Content-Type', 'application/json', 'Accept', 'application/json'),
    timeout_milliseconds := 10000
  ) into rid;
  return rid;
end $$;
revoke all on function public.brevo_post(text, jsonb) from public, anon, authenticated;

-- Send one lead to Brevo's double opt-in endpoint.
create or replace function public.brevo_push_lead(p_id bigint)
returns void language plpgsql security definer set search_path = public as $$
declare l public.leads; c public.brevo_config; rid bigint;
begin
  select * into l from public.leads where id = p_id and status = 'new';
  if not found then return; end if;
  select * into c from public.brevo_config where lang = l.lang;
  if c.doi_template_id is null then return; end if;
  rid := public.brevo_post('/contacts/doubleOptinConfirmation', jsonb_build_object(
    'email', l.email,
    'attributes', jsonb_build_object('FIRSTNAME', l.name, 'BUSINESS_TYPE', l.btype),
    'includeListIds', jsonb_build_array(c.list_id),
    'templateId', c.doi_template_id,
    'redirectionUrl', c.redirect_url));
  if rid is not null then
    update public.leads set status = 'imported', brevo_req = rid, synced_at = now() where id = p_id;
  end if;
end $$;
revoke all on function public.brevo_push_lead(bigint) from public, anon, authenticated;

-- Push right after a sign-up.
create or replace function public.leads_after_insert() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  perform public.brevo_push_lead(new.id);
  return null;
end $$;
revoke all on function public.leads_after_insert() from public, anon, authenticated;
drop trigger if exists leads_to_brevo on public.leads;
create trigger leads_to_brevo after insert on public.leads for each row execute function public.leads_after_insert();

-- Every 10 minutes: retry sign-ups that are still 'new' and mark failed calls as 'error'.
create or replace function public.brevo_sync_tick() returns void
language plpgsql security definer set search_path = public, net as $$
declare r record;
begin
  update public.leads l set status = 'error'
  from net._http_response h
  where l.status = 'imported' and l.brevo_req = h.id and (h.status_code is null or h.status_code >= 300);
  for r in select id from public.leads where status = 'new' and created_at < now() - interval '1 minute' order by id limit 50 loop
    perform public.brevo_push_lead(r.id);
  end loop;
end $$;
revoke all on function public.brevo_sync_tick() from public, anon, authenticated;
select cron.unschedule(jobid) from cron.job where jobname = 'brevo-sync';
select cron.schedule('brevo-sync', '*/10 * * * *', 'select public.brevo_sync_tick()');
