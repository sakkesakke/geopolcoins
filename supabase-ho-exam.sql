-- Human Override: teacher exam button (11 Nov 2026). Idempotent.
-- A teacher creates a "class" and gets a class code (for the pupils' browsers) and a secret teacher key.
-- With the key the teacher switches exam mode on for N minutes; joined browsers ask once a minute how long is left.
-- No accounts, no names, no e-mail: only hashes of the code and the key, and the end time of the exam.
--   public.exam_create()                      -> {"code": "ABCD2345", "key": "<64 hex>"} | {"err": "slow"}   (10 per device per hour)
--   public.exam_set(p_code, p_key, p_minutes) -> {"ok": true, "left": <seconds>} | {"err": "bad"}   (0 minutes = stop)
--   public.exam_status(p_code)                -> seconds left (0 = no exam, -1 = unknown class)
-- Classes never used for 30 days, or not used for 180 days, are deleted when a new class is made.

create table if not exists srv.ho_classes (
  code_hash  text primary key,
  key_hash   text not null,
  exam_until timestamptz,
  created_at timestamptz not null default now(),
  last_used  timestamptz not null default now()
);
alter table srv.ho_classes enable row level security;
revoke all on srv.ho_classes from anon, authenticated;

-- Abuse brake without a shared counter (a shared counter would let one sender lock out every teacher):
-- a device may make 10 classes per hour. For that hour only, a scrambled copy (hash) of its IP address is kept.
alter table srv.ho_classes add column if not exists made_by text;
create index if not exists ho_classes_made_by on srv.ho_classes (made_by) where made_by is not null;
drop table if exists srv.ho_exam_brake;

create or replace function srv.ho_hash(p text) returns text
language sql immutable set search_path = '' as
$$ select encode(sha256(convert_to('ho-exam:' || p, 'UTF8')), 'hex') $$;
revoke all on function srv.ho_hash(text) from public, anon, authenticated;

create or replace function public.exam_create() returns json
language plpgsql security definer set search_path = '' as $$
declare
  h json := coalesce(nullif(current_setting('request.headers', true), '')::json, '{}'::json);
  v_ip text := left(trim(split_part(coalesce(h->>'cf-connecting-ip', h->>'x-real-ip', h->>'x-forwarded-for', ''), ',', 1)), 64);
  v_by text := case when v_ip = '' then null else srv.ho_hash('ip:' || v_ip) end;
  abc constant text := 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';   -- 32 signs, no 0/O/1/I
  b bytea; v_code text; v_key text; i integer; tries integer := 0;
begin
  -- tidy first: forget who made a class after one hour; drop classes never used for 30 days or unused for 180 days
  update srv.ho_classes set made_by = null where made_by is not null and created_at < now() - interval '1 hour';
  delete from srv.ho_classes where last_used < now() - interval '180 days'
     or (last_used = created_at and created_at < now() - interval '30 days');
  if v_by is not null and (select count(*) from srv.ho_classes where made_by = v_by) >= 10 then return json_build_object('err', 'slow'); end if;
  if (select count(*) from srv.ho_classes where created_at > now() - interval '1 hour') >= 2000
     or (select count(*) from srv.ho_classes) >= 200000 then return json_build_object('err', 'slow'); end if;
  loop
    b := sha256(uuid_send(gen_random_uuid()) || uuid_send(gen_random_uuid()));   -- 32 evenly random bytes
    v_code := '';
    for i in 0..7 loop v_code := v_code || substr(abc, (get_byte(b, i) % 32) + 1, 1); end loop;
    v_key := replace(gen_random_uuid()::text || gen_random_uuid()::text, '-', '');
    begin
      insert into srv.ho_classes(code_hash, key_hash, made_by) values (srv.ho_hash(v_code), srv.ho_hash(v_key), v_by);
      exit;
    exception when unique_violation then
      tries := tries + 1; if tries > 5 then return json_build_object('err', 'slow'); end if;
    end;
  end loop;
  return json_build_object('code', v_code, 'key', v_key);
end $$;

-- No brake here on purpose: the key cannot be guessed (244 random bits) and a call costs one indexed update,
-- so nobody can keep a teacher from starting or stopping an exam.
create or replace function public.exam_set(p_code text, p_key text, p_minutes integer) returns json
language plpgsql security definer set search_path = '' as $$
declare v_until timestamptz; n integer;
begin
  if p_code is null or p_key is null or p_minutes is null
     or p_code !~ '^[A-HJ-NP-Z2-9]{8}$' or p_key !~ '^[0-9a-f]{64}$' or p_minutes < 0 or p_minutes > 240 then
    return json_build_object('err', 'bad');
  end if;
  v_until := case when p_minutes = 0 then null else now() + make_interval(mins => p_minutes) end;
  update srv.ho_classes set exam_until = v_until, last_used = clock_timestamp()
   where code_hash = srv.ho_hash(p_code) and key_hash = srv.ho_hash(p_key);
  get diagnostics n = row_count;
  if n = 0 then return json_build_object('err', 'bad'); end if;
  return json_build_object('ok', true, 'left', p_minutes * 60);
end $$;

create or replace function public.exam_status(p_code text) returns integer
language sql volatile security definer set search_path = '' as $$
  select case
    when p_code is null or p_code !~ '^[A-HJ-NP-Z2-9]{8}$' then -1
    else coalesce((select greatest(0, ceil(extract(epoch from (coalesce(exam_until, now()) - now())))::integer)
                     from srv.ho_classes where code_hash = srv.ho_hash(p_code)), -1)
  end $$;

revoke all on function public.exam_create() from public;
revoke all on function public.exam_set(text, text, integer) from public;
revoke all on function public.exam_status(text) from public;
grant execute on function public.exam_create() to anon, authenticated;
grant execute on function public.exam_set(text, text, integer) to anon, authenticated;
grant execute on function public.exam_status(text) to anon, authenticated;
