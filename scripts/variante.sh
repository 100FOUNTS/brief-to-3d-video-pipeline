#!/usr/bin/env bash
# Crea (o reutiliza) un worktree de git en ../estudio-lampara-<nombre> y ejecuta `make studio` allí con el brief indicado.
# Sirve para producir una variante (otra paleta, otro texto) en una carpeta aparte y a la vez, sin pisar el trabajo principal,
# y también para probar el estudio DESDE CERO (el worktree no trae ningún archivo generado).
# Uso: scripts/variante.sh <nombre> <brief.json> [make-args...]      p. ej.:  scripts/variante.sh frio brief.frio.json -j4
set -euo pipefail
[ $# -ge 2 ] || { echo "uso: scripts/variante.sh <nombre> <brief.json> [make-args]"; exit 2; }
N="$1"; B="$2"; shift 2
cd "$(dirname "$0")/.."
RAIZ="$PWD"; DEST="$(cd .. && pwd)/estudio-lampara-$N"; RAMA="variante-$N"
[ -f "$B" ] || { echo "no existe $B"; exit 2; }
if ! git diff --quiet || ! git diff --cached --quiet; then echo "Hay cambios sin commitear: haz commit antes (el worktree parte del último commit)."; exit 2; fi
if [ ! -d "$DEST" ]; then git worktree add -q -b "$RAMA" "$DEST" HEAD; fi
cd "$DEST"
# dependencias pesadas y no versionadas: se enlazan a las del proyecto principal en vez de reinstalarlas
for d in node_modules viewer/node_modules audio/.venv; do [ -e "$d" ] || ln -s "$RAIZ/$d" "$d"; done
cp "$RAIZ/$B" "./$(basename "$B")"           # el brief de la variante puede no estar aún en el commit
echo "== variante '$N' en $DEST (brief: $(basename "$B"))"
make "$@" studio BRIEF="$(basename "$B")"
