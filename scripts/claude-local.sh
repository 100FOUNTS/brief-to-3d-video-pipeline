#!/usr/bin/env bash
# Opens Claude Code against the local model (64K context). Does not change your global configuration.
# Usage: ./scripts/claude-local.sh [claude arguments]
set -e
cd "$(dirname "$0")/.."
ollama list | grep -q '^qwen3.6-64k' || ollama create qwen3.6-64k -f ollama/Modelfile.qwen3.6-64k
ANTHROPIC_BASE_URL=http://localhost:11434 ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_API_KEY="" \
  exec claude --model qwen3.6-64k "$@"
