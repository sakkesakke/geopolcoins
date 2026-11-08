#!/bin/bash
# Started every minute by cron: keeps the AI model server and the chat filter running (one copy each).
export HOME=/home/maiga OLLAMA_HOST=127.0.0.1:11434 OLLAMA_MODELS=/opt/maiga/ollama/models
B=/opt/maiga/ollama/bin/ollama
[ -s /opt/maiga/secret/server-token ] || pgrep -u "$(id -u)" -f "brain/braind.py" >/dev/null || nohup python3 /opt/maiga/repo/brain/braind.py >> /opt/maiga/logs/brain.log 2>&1 &
exit 0
if [ -x "$B" ] && ! pgrep -u "$(id -u)" -f "ollama serve" >/dev/null; then
  nohup "$B" serve >> /opt/maiga/logs/ollama.log 2>&1 &
fi
pgrep -u "$(id -u)" -f "chat/chatd.py" >/dev/null || nohup python3 /opt/maiga/repo/chat/chatd.py >> /opt/maiga/logs/chat.log 2>&1 &
pgrep -u "$(id -u)" -f "brain/braind.py" >/dev/null || nohup python3 /opt/maiga/repo/brain/braind.py >> /opt/maiga/logs/brain.log 2>&1 &
exit 0
