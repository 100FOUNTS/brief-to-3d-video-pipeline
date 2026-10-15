#!/usr/bin/env bash
# Abre Claude Code contra el modelo local (contexto de 64K). No cambia tu configuración global.
# Uso: ./scripts/claude-local.sh [argumentos de claude]
set -e
cd "$(dirname "$0")/.."
ollama list | grep -q '^qwen3.6-64k' || ollama create qwen3.6-64k -f ollama/Modelfile.qwen3.6-64k
ANTHROPIC_BASE_URL=http://localhost:11434 ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_API_KEY="" \
  exec claude --model qwen3.6-64k "$@"
