#!/usr/bin/env bash
# Opens Blender WITH a window, with the MCP add-on loaded ONLY in this session (it is not permanently enabled).
# The server listens only on localhost:9876 and has no password: close it when done (scripts/blender-live-stop.sh).
set -e
cd "$(dirname "$0")/.."
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
if lsof -nP -iTCP:9876 -sTCP:LISTEN >/dev/null 2>&1; then echo "Port 9876 is already in use: not starting."; exit 1; fi
[ -f out/blender/lamp.blend ] || { echo "out/blender/lamp.blend is missing: run 'make blender' first."; exit 1; }
cp out/blender/lamp.blend out/blender/live.blend      # work happens on a copy; the script's own file is not touched
export DISABLE_TELEMETRY=true
"$BLENDER" --factory-startup --addons blender_mcp out/blender/live.blend > out/blender/live.log 2>&1 &
echo $! > out/blender/live.pid
for i in $(seq 1 40); do
  lsof -nP -iTCP:9876 -sTCP:LISTEN >/dev/null 2>&1 && { echo "Blender ready (PID $(cat out/blender/live.pid)), MCP server on localhost:9876"; exit 0; }
  sleep 0.5
done
echo "The server did not start. See out/blender/live.log"; exit 1
