-- $MAIGA: admin access only with two-step verification (TOTP).
-- Run ONLY after the admin has set up the authenticator app on admin.html (otherwise the admin is locked out).
-- Safe to run again. To undo in an emergency: run the "undo" block at the bottom in the Supabase SQL Editor.
create or replace function public.is_admin() returns boolean
language sql stable set search_path = public as $$
  select lower(coalesce(auth.jwt() ->> 'email','')) = lower('geopolcoins1@gmail.com')
     and coalesce(auth.jwt() ->> 'aal','') = 'aal2'
$$;
-- undo (emergency only):
-- create or replace function public.is_admin() returns boolean language sql stable set search_path = public as $$
--   select lower(coalesce(auth.jwt() ->> 'email','')) = lower('geopolcoins1@gmail.com') $$;
