#!/usr/bin/env bash
# Launches ONE run of the experiment with a model and saves the session, the time and the cost report.
# Usage: experiment/phase7/launch.sh <name> <local|sonnet|opus> [effort]
set -uo pipefail
cd "$(dirname "$0")/../.."
ROOT="$PWD"; N="$1"; MODE="$2"; EFFORT="${3:-}"
D="$("$ROOT/experiment/phase7/prepare.sh" "$N")"
cd "$D"
PERMISSIONS=(--permission-mode acceptEdits --allowedTools "Bash(node:*)" "Bash(ffmpeg:*)" "Bash(ffprobe:*)" "Bash(ls:*)" "Bash(mkdir:*)" "Bash(cat:*)" "Bash(open:*)" "Read" "Write" "Edit")
EXTRA=(); [ -n "$EFFORT" ] && EXTRA=(--effort "$EFFORT")
START=$(date +%s)
case "$MODE" in
  local)  ANTHROPIC_BASE_URL=http://localhost:11434 ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_API_KEY="" \
          claude -p "$(cat prompt.md)" --model qwen3.6-64k "${PERMISSIONS[@]}" --max-turns 40 --output-format json > session.json 2> errors.txt ;;
  sonnet) claude -p "$(cat prompt.md)" --model claude-sonnet-5-5 ${EXTRA[@]+"${EXTRA[@]}"} "${PERMISSIONS[@]}" --max-turns 40 --output-format json > session.json 2> errors.txt ;;
  opus)   claude -p "$(cat prompt.md)" --model claude-opus-5-5 ${EXTRA[@]+"${EXTRA[@]}"} "${PERMISSIONS[@]}" --max-turns 40 --output-format json > session.json 2> errors.txt ;;
  *) echo "unknown mode: $MODE"; exit 2 ;;
esac
echo $(( $(date +%s) - START )) > seconds.txt
echo "finished '$N' ($MODE) in $(cat seconds.txt) s -> $D"
