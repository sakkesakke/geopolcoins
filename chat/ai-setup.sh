#!/bin/bash
# Installs Ollama (MIT) for user maiga, no root needed, and pulls the small Qwen2.5 1.5B model (Apache-2.0).
# Safe to run again: does nothing once everything is there.
set -u
D=/opt/maiga/ollama; export HOME=/home/maiga OLLAMA_HOST=127.0.0.1:11434 OLLAMA_MODELS=$D/models
mkdir -p "$D/models"
exec 9>"$D/.lock"; flock -n 9 || exit 0
if [ ! -x "$D/bin/ollama" ]; then
  echo "$(date -u +%FT%TZ) downloading ollama"
  curl -fsSL -o "$D/ollama.tgz" https://ollama.com/download/ollama-linux-arm64.tgz && tar -xzf "$D/ollama.tgz" -C "$D" && rm -f "$D/ollama.tgz" || exit 1
fi
pgrep -u "$(id -u)" -f "ollama serve" >/dev/null || { nohup "$D/bin/ollama" serve >> /opt/maiga/logs/ollama.log 2>&1 & sleep 8; }
"$D/bin/ollama" list 2>/dev/null | grep -q "qwen2.5:1.5b" || { echo "$(date -u +%FT%TZ) pulling model"; "$D/bin/ollama" pull qwen2.5:1.5b; }
echo "$(date -u +%FT%TZ) ai ready"
