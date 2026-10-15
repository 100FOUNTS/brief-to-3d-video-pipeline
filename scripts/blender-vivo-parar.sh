#!/usr/bin/env bash
# Cierra la sesión de Blender en vivo y comprueba que el puerto queda libre.
cd "$(dirname "$0")/.."
[ -f out/blender/vivo.pid ] && kill "$(cat out/blender/vivo.pid)" 2>/dev/null; rm -f out/blender/vivo.pid
sleep 1.5
if lsof -nP -iTCP:9876 -sTCP:LISTEN >/dev/null 2>&1; then echo "AVISO: el puerto 9876 sigue abierto"; lsof -nP -iTCP:9876 -sTCP:LISTEN; exit 1; else echo "Blender cerrado; puerto 9876 libre."; fi
