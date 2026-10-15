#!/usr/bin/env bash
# Prepara una carpeta aislada (FUERA del proyecto: así no le afectan sus hooks ni su CLAUDE.md) para una ejecución del experimento.
# Uso: experimento/fase7/preparar.sh <nombre>
set -euo pipefail
cd "$(dirname "$0")/../.."
RAIZ="$PWD"; N="$1"; D="$RAIZ/../experimento-fase7/$N"
[ ! -e "$D" ] || { echo "ya existe $D (bórralo o usa otro nombre)"; exit 2; }
mkdir -p "$D"
printf '{ "type": "module", "private": true }\n' > "$D/package.json"
ln -s "$RAIZ/node_modules" "$D/node_modules"            # playwright-core ya instalado
cp "$RAIZ/experimento/fase7/prompt.md" "$D/prompt.md"
cat > "$D/CLAUDE.md" <<'EOT'
# Tarea de vídeo por código
Vídeo 1920x1080 a 30 fps. Herramientas: Node 22, ffmpeg y ffprobe, Google Chrome y `playwright-core` (ya instalado en node_modules).
Después de generar un vídeo, extrae fotogramas con ffmpeg y míralos antes de decir que está listo.
EOT
echo "$D"
