# Security

$MAIGA / geopolcoins.xyz is a static site (GitHub Pages) with a Supabase back end.

## Report a problem
Found a bug that could hurt visitors or leak data? Please tell us privately:
- Email: geopolcoins1@gmail.com (subject: "Security")
- Or open a private report: Security tab > "Report a vulnerability"

Please do not post it publicly until it is fixed. We reply as soon as we can.

## What we never do
- We never ask for seed phrases, private keys or passwords. Anyone who does is not us.
- The site never connects to or moves funds from a visitor's wallet.
- No secrets live in this repository. The Supabase publishable key in the pages is public by design;
  all data access is limited by row level security and rate limits.

## Scope
In scope: geopolcoins.xyz pages, the Supabase functions they call.
Out of scope: third-party sites we link to (Jupiter, DEX Screener, Ko-fi, X, AI providers).
