#!/bin/bash
# Started every minute by cron: keeps the AI model server, the chat filter and The Brain running (one copy each).
export HOME=/home/maiga OLLAMA_HOST=127.0.0.1:11434 OLLAMA_MODELS=/opt/maiga/ollama/models OLLAMA_NUM_PARALLEL=2
B=/opt/maiga/ollama/bin/ollama
[ -s /opt/maiga/secret/server-token ] || exit 0
if [ -x "$B" ] && ! pgrep -u "$(id -u)" -f "ollama serve" >/dev/null; then
  nohup "$B" serve >> /opt/maiga/logs/ollama.log 2>&1 &
fi
pgrep -u "$(id -u)" -f "chat/chatd.py" >/dev/null || nohup python3 /opt/maiga/repo/chat/chatd.py >> /opt/maiga/logs/chat.log 2>&1 &
if [ -f /opt/maiga/repo/brain/DISABLED ]; then
  pkill -u "$(id -u)" -f "brain/braind.py" 2>/dev/null
else
  pgrep -u "$(id -u)" -f "brain/braind.py" >/dev/null || nohup python3 /opt/maiga/repo/brain/braind.py >> /opt/maiga/logs/brain.log 2>&1 &
fi
exit 0
