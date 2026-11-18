Proof-of-date files (OpenTimestamps), made automatically by .github/workflows/proof.yml.
Each .txt lists SHA-256 fingerprints of the files at one commit; the .ots next to it proves the date.
Check: pip install opentimestamps-client && ots verify <file>.txt.ots
