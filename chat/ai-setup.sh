#!/bin/bash
# Installs Ollama (MIT) for user maiga, no root needed, and pulls the small Qwen2.5 1.5B model (Apache-2.0).
# Safe to run again: does nothing once everything is there.
set -u
D=/opt/maiga/ollama; export HOME=/home/maiga OLLAMA_HOST=127.0.0.1:11434 OLLAMA_MODELS=$D/models
mkdir -p "$D/models"
exec 9>"$D/.lock"; flock -n 9 || exit 0
if [ ! -x "$D/bin/ollama" ]; then
  echo "$(date -u +%FT%TZ) downloading ollama"
  U=https://ollama.com/download/ollama-linux-arm64
  if command -v zstd >/dev/null && curl -fsI -L "$U.tar.zst" >/dev/null; then
    curl -fsSL "$U.tar.zst" | zstd -d | tar -xf - -C "$D" || { echo "zst download failed"; exit 1; }
  elif curl -fsI -L "$U.tgz" >/dev/null; then
    curl -fsSL "$U.tgz" | tar -xzf - -C "$D" || { echo "tgz download failed"; exit 1; }
  else
    echo "no usable download (zstd installed: $(command -v zstd || echo no))"; exit 1
  fi
fi
pgrep -u "$(id -u)" -f "ollama serve" >/dev/null || { nohup "$D/bin/ollama" serve >> /opt/maiga/logs/ollama.log 2>&1 & sleep 8; }
"$D/bin/ollama" list 2>/dev/null | grep -q "qwen2.5:1.5b" || { echo "$(date -u +%FT%TZ) pulling model"; "$D/bin/ollama" pull qwen2.5:1.5b; }
echo "$(date -u +%FT%TZ) ai ready"
