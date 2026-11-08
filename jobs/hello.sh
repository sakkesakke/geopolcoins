#!/bin/bash
# Check in with the geopolcoins.xyz database every 10 minutes.
# The token is made here once, stays only on this server (chmod 600) and is never printed or committed;
# the database stores only its sha256. The key below is the public "publishable" key the website uses.
set -u
D=/opt/maiga/secret; T=$D/server-token
mkdir -p "$D"; chmod 700 "$D"
[ -s "$T" ] || { (umask 077; openssl rand -hex 32 > "$T"); }
INFO=$(jq -nc --arg up "$(uptime -p)" --arg load "$(cut -d' ' -f1-3 /proc/loadavg)" \
  --arg mem "$(free -m | awk '/Mem:/{print $3"/"$2" MB"}')" --arg disk "$(df -h / | awk 'NR==2{print $3"/"$2}')" \
  --arg rev "$(git -C /opt/maiga/repo rev-parse --short HEAD)" \
  --arg ai "$(curl -s -m 3 http://127.0.0.1:11434/api/tags | jq -r '[.models[]?.name]|join(",")' 2>/dev/null || echo off)" \
  --arg chat "$(tail -n 200 /opt/maiga/logs/chat.log 2>/dev/null | awk '{print $3}' | sort | uniq -c | tr -s ' ' | tr '\n' ';')" \
  --arg radar "$(tail -n 1 /opt/maiga/logs/radar.log 2>/dev/null | cut -c1-160)" \
  --arg setup "$(tail -n 2 /opt/maiga/logs/ai-setup.log 2>/dev/null | tr '\n' ' ' | cut -c1-200)" \
  '{uptime:$up, load:$load, mem:$mem, disk:$disk, rev:$rev, ai:$ai, chat:$chat, setup:$setup, radar:$radar}')
BODY=$(jq -nc --arg t "$(cat "$T")" --argjson i "$INFO" '{p_id:"maiga-server", p_token:$t, p_info:$i}')
R=$(curl -s -m 20 -X POST "https://zslzbfbqrtfpvgbjhssd.supabase.co/rest/v1/rpc/server_hello" \
  -H "apikey: sb_publishable_90hLwzv3xb0aZmPtaHKZag_1hKkG0EN" -H "Content-Type: application/json" -d "$BODY")
echo "$(date -u +%FT%TZ) hello $R"
