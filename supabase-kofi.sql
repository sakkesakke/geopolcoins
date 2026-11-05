-- Ko-fi -> CRM. Every Ko-fi donation, shop order, subscription or commission is stored once and
-- the buyer is added to (or updated in) the CRM as a customer.
-- Called only by the Edge Function 'kofi-webhook' (service role), which checks Ko-fi's verification token.
-- Safe to run again.

create table if not exists public.kofi_sales (
  message_id      text primary key check (char_length(message_id) between 1 and 80),
  received_at     timestamptz not null default now(),
  kofi_time       timestamptz,
  type            text not null default '' check (char_length(type) <= 40),
  amount          numeric(12,2) not null default 0 check (amount >= 0 and amount < 1000000),
  currency        text not null default '' check (char_length(currency) <= 8),
  from_name       text not null default '' check (char_length(from_name) <= 120),
  email           text not null default '' check (char_length(email) <= 120),
  message         text not null default '' check (char_length(message) <= 1000),
  items           jsonb not null default '[]'::jsonb,
  transaction_id  text not null default '' check (char_length(transaction_id) <= 80),
  is_public       boolean not null default false,
  contact_id      bigint references public.crm_contacts(id) on delete set null
);
alter table public.kofi_sales enable row level security;
revoke all on public.kofi_sales from anon, authenticated;
grant select on public.kofi_sales to authenticated;
drop policy if exists "admin reads kofi sales" on public.kofi_sales;
create policy "admin reads kofi sales" on public.kofi_sales for select to authenticated using ((select public.is_admin()));
create index if not exists kofi_sales_contact_idx on public.kofi_sales (contact_id);
create index if not exists kofi_sales_received_idx on public.kofi_sales (received_at desc);

create or replace function public.kofi_record(p jsonb)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_mid    text := left(coalesce(p->>'message_id', ''), 80);
  v_email  text := lower(left(trim(coalesce(p->>'email', '')), 120));
  v_name   text := left(trim(coalesce(p->>'from_name', '')), 80);
  v_type   text := left(coalesce(p->>'type', ''), 40);
  v_cur    text := upper(left(coalesce(p->>'currency', ''), 8));
  v_amount numeric(12,2);
  v_items  jsonb := case when jsonb_typeof(p->'shop_items') = 'array' then p->'shop_items' else '[]'::jsonb end;
  v_cid    bigint;
  v_new    boolean := false;
  v_what   text;
begin
  if v_mid = '' then
    raise exception 'missing message_id';
  end if;
  begin
    v_amount := greatest(0, least(999999, coalesce(nullif(p->>'amount', '')::numeric, 0)));
  exception when others then
    v_amount := 0;
  end;
  -- Ko-fi retries: store each message once
  if exists (select 1 from public.kofi_sales where message_id = v_mid) then
    return jsonb_build_object('ok', true, 'duplicate', true);
  end if;

  v_what := v_type || ' ' || v_amount::text || ' ' || v_cur
            || case when jsonb_array_length(v_items) > 0
                    then ' (' || (select string_agg(coalesce(i->>'direct_link_code', '?') || ' x' || coalesce(i->>'quantity', '1'), ', ')
                                  from jsonb_array_elements(v_items) i) || ')'
                    else '' end;

  if v_email <> '' then
    select id into v_cid from public.crm_contacts where lower(email) = v_email order by id limit 1;
  end if;
  if v_cid is null then
    insert into public.crm_contacts (name, email, kind, segment, source, stage, lang, next_action, next_date, tags, first_message, value_eur)
    values (v_name, v_email, 'customer', 'other', 'kofi', 'won', 'en',
            'Say thanks, ask how the pack works for them', current_date,
            array['kofi', lower(replace(v_type, ' ', '-'))],
            left('Ko-fi: ' || v_what || coalesce(nullif(E'\n' || left(coalesce(p->>'message', ''), 600), E'\n'), ''), 1600),
            case when v_cur = 'EUR' then v_amount else 0 end)
    returning id into v_cid;
    v_new := true;
  else
    update public.crm_contacts c
       set kind = 'customer',
           stage = case when c.stage in ('lost', 'new', 'contacted', 'quote', 'nurture') then 'won' else c.stage end,
           value_eur = least(9999999, c.value_eur + case when v_cur = 'EUR' then v_amount else 0 end),
           tags = (array(select distinct t from unnest(c.tags || array['kofi']) t))[1:12],
           next_action = 'Say thanks for the new Ko-fi ' || lower(v_type),
           next_date = current_date,
           updated_at = now()
     where c.id = v_cid;
  end if;

  insert into public.kofi_sales (message_id, kofi_time, type, amount, currency, from_name, email, message, items, transaction_id, is_public, contact_id)
  values (v_mid,
          case when coalesce(p->>'timestamp', '') ~ '^\d{4}-\d{2}-\d{2}T' then (p->>'timestamp')::timestamptz else null end,
          v_type, v_amount, v_cur, left(coalesce(p->>'from_name', ''), 120), v_email,
          left(coalesce(p->>'message', ''), 1000), v_items,
          left(coalesce(p->>'kofi_transaction_id', ''), 80),
          lower(coalesce(p->>'is_public', '')) = 'true', v_cid);

  return jsonb_build_object('ok', true, 'contact_id', v_cid, 'new_contact', v_new);
end;
$$;

revoke all on function public.kofi_record(jsonb) from public, anon, authenticated;
grant execute on function public.kofi_record(jsonb) to service_role;
