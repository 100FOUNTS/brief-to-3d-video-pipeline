#!/usr/bin/env bash
# Lanza UNA ejecución del experimento con un modelo y guarda la sesión, el tiempo y el informe de coste.
# Uso: experimento/fase7/lanzar.sh <nombre> <local|sonnet|opus> [effort]
set -uo pipefail
cd "$(dirname "$0")/../.."
RAIZ="$PWD"; N="$1"; MODO="$2"; EFFORT="${3:-}"
D="$("$RAIZ/experimento/fase7/preparar.sh" "$N")"
cd "$D"
PERMISOS=(--permission-mode acceptEdits --allowedTools "Bash(node:*)" "Bash(ffmpeg:*)" "Bash(ffprobe:*)" "Bash(ls:*)" "Bash(mkdir:*)" "Bash(cat:*)" "Bash(open:*)" "Read" "Write" "Edit")
EXTRA=(); [ -n "$EFFORT" ] && EXTRA=(--effort "$EFFORT")
INICIO=$(date +%s)
case "$MODO" in
  local)  ANTHROPIC_BASE_URL=http://localhost:11434 ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_API_KEY="" \
          claude -p "$(cat prompt.md)" --model qwen3.6-64k "${PERMISOS[@]}" --max-turns 40 --output-format json > sesion.json 2> errores.txt ;;
  sonnet) claude -p "$(cat prompt.md)" --model claude-sonnet-5-5 ${EXTRA[@]+"${EXTRA[@]}"} "${PERMISOS[@]}" --max-turns 40 --output-format json > sesion.json 2> errores.txt ;;
  opus)   claude -p "$(cat prompt.md)" --model claude-opus-5-5 ${EXTRA[@]+"${EXTRA[@]}"} "${PERMISOS[@]}" --max-turns 40 --output-format json > sesion.json 2> errores.txt ;;
  *) echo "modo desconocido: $MODO"; exit 2 ;;
esac
echo $(( $(date +%s) - INICIO )) > segundos.txt
echo "terminó '$N' ($MODO) en $(cat segundos.txt) s -> $D"
