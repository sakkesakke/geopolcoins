-- Live chat (owner chose option 3, 2026-11-07): visitors send text, the Oracle server filters every
-- message (links/domains/addresses removed, scam words, swearing, plus a small local AI model) and only
-- then publishes it. Visitors can never write to chat_messages directly.

create table if not exists srv.chat_inbox (
  id bigserial primary key,
  room text not null,
  name text not null,
  body text not null,
  client text not null,
  ip text,
  at timestamptz not null default now(),
  status text not null default 'pending'   -- pending | taken | ok | blocked
);
create index if not exists chat_inbox_status on srv.chat_inbox (status, id);
create index if not exists chat_inbox_client on srv.chat_inbox (client, at);
alter table srv.chat_inbox enable row level security;

create table if not exists srv.chat_reports (
  msg_id bigint not null,
  client text not null,
  at timestamptz not null default now(),
  primary key (msg_id, client)
);
alter table srv.chat_reports enable row level security;

create table if not exists public.chat_messages (
  id bigint primary key,            -- same id as the inbox row
  room text not null,
  name text not null,
  body text not null,
  at timestamptz not null default now(),
  hidden boolean not null default false
);
create index if not exists chat_messages_room on public.chat_messages (room, id);
alter table public.chat_messages enable row level security;
revoke all on public.chat_messages from anon, authenticated;
grant select (id, room, name, body, at) on public.chat_messages to anon, authenticated;
drop policy if exists "chat read recent visible" on public.chat_messages;
create policy "chat read recent visible" on public.chat_messages for select to anon, authenticated
  using (not hidden and at > now() - interval '2 days');

-- is the filter server alive? (chat closes itself when the server is down)
create or replace function srv.server_alive() returns boolean language sql stable security definer set search_path = '' as $$
  select exists (select 1 from srv.servers where id = 'maiga-server' and last_seen > now() - interval '15 minutes')
$$;

create or replace function srv.server_ok(p_token text) returns boolean language sql stable security definer set search_path = '' as $$
  select exists (select 1 from srv.servers where id = 'maiga-server'
                 and token_hash = encode(extensions.digest(coalesce(p_token, ''), 'sha256'), 'hex'))
$$;

create or replace function public.chat_status() returns text language sql stable security definer set search_path = '' as $$
  select case when srv.server_alive() then 'open' else 'closed' end
$$;

create or replace function public.chat_send(p_room text, p_name text, p_body text, p_client text)
returns text language plpgsql security definer set search_path = '' as $$
declare
  h json := coalesce(nullif(current_setting('request.headers', true), '')::json, '{}'::json);
  v_ip text := left(trim(split_part(coalesce(h->>'cf-connecting-ip', h->>'x-real-ip', h->>'x-forwarded-for', ''), ',', 1)), 64);
  b text := btrim(regexp_replace(coalesce(p_body, ''), '[[:cntrl:]]', ' ', 'g'));
begin
  if p_room not in ('site', 'world') or coalesce(p_name, '') !~ '^[A-Za-z0-9 _-]{1,16}$'
     or length(b) < 1 or length(b) > 200 or coalesce(p_client, '') !~ '^[a-z0-9]{8,32}$' then
    return 'bad';
  end if;
  if not srv.server_alive() then return 'closed'; end if;
  if exists (select 1 from srv.chat_inbox where (client = p_client or (v_ip <> '' and ip = v_ip)) and at > now() - interval '6 seconds')
     or (select count(*) from srv.chat_inbox where (client = p_client or (v_ip <> '' and ip = v_ip)) and at > now() - interval '10 minutes') >= 25 then
    return 'slow';
  end if;
  if (select count(*) from srv.chat_inbox where at > now() - interval '1 minute') >= 120 then
    return 'busy';
  end if;
  insert into srv.chat_inbox(room, name, body, client, ip) values (p_room, btrim(p_name), b, p_client, v_ip);
  return 'queued';
end $$;

create or replace function public.chat_report(p_id bigint, p_client text) returns text
language plpgsql security definer set search_path = '' as $$
begin
  if coalesce(p_client, '') !~ '^[a-z0-9]{8,32}$' then return 'bad'; end if;
  if not exists (select 1 from public.chat_messages where id = p_id) then return 'bad'; end if;
  insert into srv.chat_reports(msg_id, client) values (p_id, p_client) on conflict do nothing;
  if (select count(*) from srv.chat_reports where msg_id = p_id) >= 3 then
    update public.chat_messages set hidden = true where id = p_id;
    return 'hidden';
  end if;
  return 'ok';
end $$;

-- server side: take pending messages, then publish or block them
create or replace function public.server_chat_pull(p_token text) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare r jsonb;
begin
  if not srv.server_ok(p_token) then return '[]'::jsonb; end if;
  update srv.chat_inbox set status = 'pending' where status = 'taken' and at < now() - interval '2 minutes';
  with t as (
    update srv.chat_inbox set status = 'taken'
    where id in (select id from srv.chat_inbox where status = 'pending' order by id limit 50 for update skip locked)
    returning id, room, name, body
  ) select coalesce(jsonb_agg(to_jsonb(t) order by t.id), '[]'::jsonb) into r from t;
  return r;
end $$;

create or replace function public.server_chat_verdict(p_token text, p_items jsonb) returns int
language plpgsql security definer set search_path = '' as $$
declare it jsonb; n int := 0; m srv.chat_inbox%rowtype;
begin
  if not srv.server_ok(p_token) then return -1; end if;
  for it in select * from jsonb_array_elements(coalesce(p_items, '[]'::jsonb)) loop
    select * into m from srv.chat_inbox where id = (it->>'id')::bigint and status = 'taken';
    continue when not found;
    if (it->>'ok')::boolean and length(coalesce(it->>'body', '')) between 1 and 200 then
      insert into public.chat_messages(id, room, name, body) values (m.id, m.room, m.name, it->>'body') on conflict do nothing;
      update srv.chat_inbox set status = 'ok' where id = m.id;
      n := n + 1;
    else
      update srv.chat_inbox set status = 'blocked' where id = m.id;
    end if;
  end loop;
  delete from public.chat_messages where at < now() - interval '2 days';
  delete from srv.chat_inbox where at < now() - interval '1 day';
  delete from srv.chat_reports where at < now() - interval '2 days';
  return n;
end $$;

revoke all on function srv.server_alive(), srv.server_ok(text) from public;
revoke all on function public.chat_status(), public.chat_send(text, text, text, text), public.chat_report(bigint, text),
  public.server_chat_pull(text), public.server_chat_verdict(text, jsonb) from public;
grant execute on function public.chat_status(), public.chat_send(text, text, text, text), public.chat_report(bigint, text),
  public.server_chat_pull(text), public.server_chat_verdict(text, jsonb) to anon, authenticated;

-- 2026-11-08 hardening (applied as migration hardening_hello_and_reports):
--  * server_hello checks a valid token first, so flooding the function cannot block the real server's check-in;
--  * chat_report counts reports per IP (max 10 per IP per hour), so one person cannot hide messages alone.
-- 2026-11-08 Rug Radar 24/7 (migration radar_live): public.radar_live (read-only for visitors, one row),
--  srv.radar_daily, public.server_radar_push(p_token, p_stats) for the server only.
