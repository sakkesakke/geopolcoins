#!/bin/sh
# Mindveto for Mac and Linux - the AI kill switch
# Copyright (c) 2026 Amghar Said. All rights reserved.
# Blocks AI services for every browser and app on this computer via /etc/hosts.
#   sudo sh mindveto.sh on     block AI (or update the list)
#   sudo sh mindveto.sh off    allow AI again
#   sudo sh mindveto.sh family-on    family filter: block adult sites (18+) and force SafeSearch
#   sudo sh mindveto.sh family-off   switch the family filter off
set -eu
HOSTS=/etc/hosts
START='# >>> Human Override (do not edit this block)'
END='# <<< Human Override'
URL='https://geopolcoins.xyz/human-override/hosts.txt'
FSTART='# >>> Mindveto family filter (do not edit this block)'
FEND='# <<< Mindveto family filter'
AURL='https://geopolcoins.xyz/human-override/adult/hosts.txt'
[ "$(id -u)" -eq 0 ] || { echo "Run with sudo:  sudo sh $0 on"; exit 1; }
strip() { awk -v s="${1:-$START}" -v e="${2:-$END}" '$0==s{skip=1;next} $0==e{skip=0;next} !skip' "$HOSTS"; }
# address of a search engine's official strict server (looked up now, so it stays correct)
ip4() { { dig +short A "$1" 2>/dev/null; host -t A "$1" 2>/dev/null | awk '/has address/{print $4}'; getent ahostsv4 "$1" 2>/dev/null | awk '{print $1}';
          dscacheutil -q host -a name "$1" 2>/dev/null | awk '/ip_address/{print $2}'; } | grep -E '^[0-9]{1,3}(\.[0-9]{1,3}){3}$' | head -1 || true; }
safe_lines() {
  for pair in "forcesafesearch.google.com:google.com www.google.com www.google.be www.google.nl www.google.fr www.google.de www.google.es www.google.it www.google.pt www.google.co.uk www.google.co.ma www.google.com.br www.google.ca" \
              "strict.bing.com:bing.com www.bing.com" "safe.duckduckgo.com:duckduckgo.com www.duckduckgo.com start.duckduckgo.com html.duckduckgo.com" \
              "restrict.youtube.com:www.youtube.com m.youtube.com youtubei.googleapis.com youtube.googleapis.com www.youtube-nocookie.com"; do
    T=${pair%%:*}; IP=$(ip4 "$T")
    if [ -n "$IP" ]; then for n in ${pair#*:}; do echo "$IP $n"; done; fi
  done
  true
}
flush() { (dscacheutil -flushcache 2>/dev/null; killall -HUP mDNSResponder 2>/dev/null; resolvectl flush-caches 2>/dev/null) || true; }
case "${1:-on}" in
  on)
    if [ "${2:-}" != "--agree" ]; then
      echo "Terms: Mindveto is provided \"as is\" and cannot guarantee that every AI is blocked."
      echo "To the maximum extent permitted by law, Amghar Said is not liable for any damage or consequence of using it."
      echo "Full terms: https://mindveto.app/terms/"
      printf "Type Y to agree and continue: "; read -r A
      case "$A" in [YyJj]*) ;; *) echo "Nothing was changed."; exit 1 ;; esac
    fi
    TMP=$(mktemp)
    if ! curl -fsSL --max-time 20 "$URL" -o "$TMP" 2>/dev/null; then
      [ -f "$(dirname "$0")/hosts.txt" ] && cp "$(dirname "$0")/hosts.txt" "$TMP" || { echo "Could not download the list."; exit 1; }
    fi
    LINES=$(grep -E '^0\.0\.0\.0 ([a-z0-9-]{1,63}\.)+[a-z]{2,24}$' "$TMP" || true)
    N=$(printf '%s\n' "$LINES" | grep -c . || true)
    [ "$N" -ge 20 ] || { echo "The list looks wrong. Nothing changed."; rm -f "$TMP"; exit 1; }
    cp "$HOSTS" "$HOSTS.human-override-backup"
    { strip; echo "$START"; printf '%s\n' "$LINES"; echo "$END"; } > "$TMP.new"
    cat "$TMP.new" > "$HOSTS"; rm -f "$TMP" "$TMP.new"; flush
    echo "Done: $N AI addresses blocked. Restart your browser." ;;
  off)
    TMP=$(mktemp); strip > "$TMP"; cat "$TMP" > "$HOSTS"; rm -f "$TMP"; flush
    echo "AI is allowed again." ;;
  family-on)
    TMP=$(mktemp)
    if ! curl -fsSL --max-time 60 "$AURL" -o "$TMP" 2>/dev/null; then
      [ -f "$(dirname "$0")/adult-hosts.txt" ] && cp "$(dirname "$0")/adult-hosts.txt" "$TMP" || { echo "Could not download the family filter list."; exit 1; }
    fi
    LINES=$(grep -E '^0\.0\.0\.0 ([a-z0-9-]{1,63}\.)+[a-z]{2,24}$' "$TMP" || true)
    N=$(printf '%s\n' "$LINES" | grep -c . || true)
    [ "$N" -ge 1000 ] || { echo "The family filter list looks wrong. Nothing changed."; rm -f "$TMP"; exit 1; }
    SAFE=$(safe_lines)
    cp "$HOSTS" "$HOSTS.human-override-backup"
    { strip "$FSTART" "$FEND"; echo "$FSTART"; if [ -n "$SAFE" ]; then printf '%s\n' "$SAFE"; fi; printf '%s\n' "$LINES"; echo "$FEND"; } > "$TMP.new"
    cat "$TMP.new" > "$HOSTS"; rm -f "$TMP" "$TMP.new"; flush
    echo "Done: $N adult addresses blocked. Restart your browser."
    if [ -n "$SAFE" ]; then echo "SafeSearch is forced for Google, Bing, DuckDuckGo and YouTube."; else echo "SafeSearch could not be set (no internet?). Run family-on again later."; fi ;;
  family-off)
    TMP=$(mktemp); strip "$FSTART" "$FEND" > "$TMP"; cat "$TMP" > "$HOSTS"; rm -f "$TMP"; flush
    echo "Family filter switched off." ;;
  *) echo "Use: sudo sh $0 on|off|family-on|family-off"; exit 1 ;;
esac
