#!/usr/bin/env bash
# Prepares an isolated folder (OUTSIDE the project, so its hooks and its CLAUDE.md do not affect it) for one run of the experiment.
# Usage: experiment/phase7/prepare.sh <name>
set -euo pipefail
cd "$(dirname "$0")/../.."
ROOT="$PWD"; N="$1"; D="$ROOT/../experiment-phase7/$N"
[ ! -e "$D" ] || { echo "$D already exists (delete it or use another name)"; exit 2; }
mkdir -p "$D"
printf '{ "type": "module", "private": true }\n' > "$D/package.json"
ln -s "$ROOT/node_modules" "$D/node_modules"            # playwright-core is already installed
cp "$ROOT/experiment/phase7/prompt.md" "$D/prompt.md"
# The CLAUDE.md below is part of the experiment's INPUT, so it stays in Spanish exactly as the models received it.
cat > "$D/CLAUDE.md" <<'EOT'
# Tarea de vídeo por código
Vídeo 1920x1080 a 30 fps. Herramientas: Node 22, ffmpeg y ffprobe, Google Chrome y `playwright-core` (ya instalado en node_modules).
Después de generar un vídeo, extrae fotogramas con ffmpeg y míralos antes de decir que está listo.
EOT
echo "$D"
