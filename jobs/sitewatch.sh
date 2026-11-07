#!/bin/bash
# Checks that the main pages answer. One line per check: time, page, HTTP code, seconds.
for p in "" hq.html blog.html; do
  r=$(curl -s -o /dev/null -m 20 -w "%{http_code} %{time_total}" "https://geopolcoins.xyz/$p" || echo "000 0")
  echo "$(date -u +%FT%TZ) /$p $r"
done
