#!/usr/bin/env bash
# Closes the live Blender session and checks that the port is free again.
cd "$(dirname "$0")/.."
[ -f out/blender/live.pid ] && kill "$(cat out/blender/live.pid)" 2>/dev/null; rm -f out/blender/live.pid
sleep 1.5
if lsof -nP -iTCP:9876 -sTCP:LISTEN >/dev/null 2>&1; then echo "WARNING: port 9876 is still open"; lsof -nP -iTCP:9876 -sTCP:LISTEN; exit 1; else echo "Blender closed; port 9876 free."; fi
