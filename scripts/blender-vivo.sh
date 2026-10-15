#!/usr/bin/env bash
# Abre Blender CON ventana, con el complemento MCP cargado SOLO en esta sesión (no se activa de forma permanente).
# El servidor escucha únicamente en localhost:9876 y no tiene contraseña: ciérralo al terminar (scripts/blender-vivo-parar.sh).
set -e
cd "$(dirname "$0")/.."
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
if lsof -nP -iTCP:9876 -sTCP:LISTEN >/dev/null 2>&1; then echo "El puerto 9876 ya está en uso: no arranco."; exit 1; fi
[ -f out/blender/lampara.blend ] || { echo "Falta out/blender/lampara.blend: ejecuta antes 'make blender'."; exit 1; }
cp out/blender/lampara.blend out/blender/vivo.blend      # se trabaja sobre una copia; la del script no se toca
export DISABLE_TELEMETRY=true
"$BLENDER" --factory-startup --addons blender_mcp out/blender/vivo.blend > out/blender/vivo.log 2>&1 &
echo $! > out/blender/vivo.pid
for i in $(seq 1 40); do
  lsof -nP -iTCP:9876 -sTCP:LISTEN >/dev/null 2>&1 && { echo "Blender listo (PID $(cat out/blender/vivo.pid)), servidor MCP en localhost:9876"; exit 0; }
  sleep 0.5
done
echo "El servidor no arrancó. Mira out/blender/vivo.log"; exit 1
