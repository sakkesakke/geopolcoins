#!/bin/sh
# Mindveto for Mac and Linux - the AI kill switch
# Copyright (c) 2026 Amghar Said. All rights reserved.
# Blocks AI services for every browser and app on this computer via /etc/hosts.
#   sudo sh human-override.sh on     block AI (or update the list)
#   sudo sh human-override.sh off    allow AI again
set -eu
HOSTS=/etc/hosts
START='# >>> Human Override (do not edit this block)'
END='# <<< Human Override'
URL='https://geopolcoins.xyz/human-override/hosts.txt'
[ "$(id -u)" -eq 0 ] || { echo "Run with sudo:  sudo sh $0 on"; exit 1; }
strip() { awk -v s="$START" -v e="$END" '$0==s{skip=1;next} $0==e{skip=0;next} !skip' "$HOSTS"; }
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
  *) echo "Use: sudo sh $0 on|off"; exit 1 ;;
esac
