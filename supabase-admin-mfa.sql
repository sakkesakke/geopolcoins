-- $MAIGA: admin access only with two-step verification (TOTP). Applied 2026-11-10 after the owner set up 2FA.
-- Admin = the owner's fixed user id + email + email login + a session that passed 2FA (aal2).
-- To undo in an emergency: run the "undo" block at the bottom in the Supabase SQL Editor.
create or replace function public.is_admin() returns boolean
language sql stable set search_path = public as $$
  select (select auth.uid()) = 'f22fd754-e06a-4fb3-b4e5-3c2342a4f383'::uuid
     and lower(coalesce(auth.jwt() ->> 'email','')) = lower('geopolcoins1@gmail.com')
     and coalesce(auth.jwt() -> 'app_metadata' ->> 'provider', '') = 'email'
     and coalesce(auth.jwt() ->> 'aal','') = 'aal2'
$$;
-- undo (emergency only, removes the 2FA requirement):
-- create or replace function public.is_admin() returns boolean language sql stable set search_path = public as $$
--   select (select auth.uid()) = 'f22fd754-e06a-4fb3-b4e5-3c2342a4f383'::uuid
--      and lower(coalesce(auth.jwt() ->> 'email','')) = lower('geopolcoins1@gmail.com')
--      and coalesce(auth.jwt() -> 'app_metadata' ->> 'provider', '') = 'email' $$;
