-- $MAIGA Bot Garage: community bots, likes and copies.
-- Paste this whole file once in Supabase > SQL Editor > New query > Run.
-- Safe to run again. It only creates new things; it does not change or delete existing data.

create table if not exists public.garage_bots (
  id bigserial primary key,
  created_at timestamptz not null default now(),
  nickname text not null check (nickname ~ '^[A-Za-z0-9_.-]{2,20}$'),
  name text not null check (char_length(name) between 1 and 28),
  cat text not null check (cat in ('crypto','business','creator','life')),
  role text not null default '' check (char_length(role) <= 120),
  recipe jsonb not null check (jsonb_typeof(recipe) = 'object' and octet_length(recipe::text) <= 4000),
  likes integer not null default 0,
  copies integer not null default 0,
  hidden boolean not null default false
);
create index if not exists garage_bots_likes_idx on public.garage_bots (likes desc, created_at desc) where hidden = false;
create index if not exists garage_bots_new_idx on public.garage_bots (created_at desc) where hidden = false;
create table if not exists public.garage_brake (minute timestamptz primary key, n integer not null default 0);

alter table public.garage_bots enable row level security;
alter table public.garage_brake enable row level security;

revoke all on public.garage_bots from anon, authenticated;
revoke all on public.garage_brake from anon, authenticated;
grant select (id, created_at, nickname, name, cat, role, recipe, likes, copies) on public.garage_bots to anon, authenticated;
grant insert (nickname, name, cat, role, recipe) on public.garage_bots to anon, authenticated;
grant usage, select on sequence public.garage_bots_id_seq to anon, authenticated;
grant update (hidden), delete on public.garage_bots to authenticated;  -- only the admin policy below lets this through

drop policy if exists gb_read on public.garage_bots;
drop policy if exists gb_add on public.garage_bots;
drop policy if exists gb_admin on public.garage_bots;
create policy gb_read on public.garage_bots for select to anon, authenticated using (hidden = false);
create policy gb_add on public.garage_bots for insert to anon, authenticated with check (hidden = false and likes = 0 and copies = 0);
create policy gb_admin on public.garage_bots for all to authenticated using (public.is_admin()) with check (public.is_admin());

-- Limits and anti-scam filter for new bots
create or replace function public.gb_limit() returns trigger
language plpgsql security definer set search_path = public as $$
declare txt text := lower(new.name || ' ' || new.role || ' ' || new.recipe::text);
begin
  if (select count(*) from public.garage_bots where created_at > now() - interval '1 hour') >= 30 then
    raise exception 'The garage is busy right now. Try again in a while.';
  end if;
  if (select count(*) from public.garage_bots where lower(nickname) = lower(new.nickname) and created_at > now() - interval '1 day') >= 5 then
    raise exception 'Max 5 bots per nickname per day.';
  end if;
  if regexp_replace(txt, 'https?://(www\.)?geopolcoins\.xyz[^\s"]*', '', 'g') ~ '(https?://|www\.|t\.me/|discord\.gg|bit\.ly|\.ru/)' then
    raise exception 'Links are not allowed in shared bots (only geopolcoins.xyz).';
  end if;
  if txt ~ '(send me (your )?(sol|crypto|tokens)|guaranteed (profit|returns)|dm me your (seed|key))' then
    raise exception 'This bot contains words we do not allow in the community garage.';
  end if;
  new.likes := 0; new.copies := 0; new.hidden := false;
  return new;
end $$;
revoke all on function public.gb_limit() from public, anon, authenticated;
drop trigger if exists gb_limit_trg on public.garage_bots;
create trigger gb_limit_trg before insert on public.garage_bots for each row execute function public.gb_limit();

-- Likes and copies, with a global brake against floods
create or replace function public.garage_bump(p_id bigint, p_kind text) returns void
language plpgsql security definer set search_path = public as $$
declare m timestamptz := date_trunc('minute', now()); c integer;
begin
  if p_kind not in ('like','copy') then raise exception 'bad kind'; end if;
  insert into public.garage_brake(minute, n) values (m, 0) on conflict (minute) do nothing;
  update public.garage_brake set n = n + 1 where minute = m returning n into c;
  delete from public.garage_brake where minute < now() - interval '1 hour';
  if c > 240 then raise exception 'Too busy right now. Try again in a minute.'; end if;
  if p_kind = 'like' then
    update public.garage_bots set likes = likes + 1 where id = p_id and hidden = false and likes < 1000000;
  else
    update public.garage_bots set copies = copies + 1 where id = p_id and hidden = false and copies < 1000000;
  end if;
end $$;
revoke all on function public.garage_bump(bigint, text) from public;
grant execute on function public.garage_bump(bigint, text) to anon, authenticated;
