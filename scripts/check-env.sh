#!/usr/bin/env bash
# Checks that the environment is ready.
ok=0
check() {
  local name="$1"; shift
  if out=$("$@" 2>&1 | head -1); then printf "  OK   %-10s %s\n" "$name" "$out"; else printf "  MISSING %-7s\n" "$name"; ok=1; fi
}
echo "Tools:"
check node node --version
check npm npm --version
check ffmpeg bash -c 'ffmpeg -version | head -1'
check python3 python3 --version
check uv uv --version
check claude claude --version
check git git --version
if [ -x /Applications/Blender.app/Contents/MacOS/Blender ]; then
  printf "  OK   %-10s %s\n" blender "$(/Applications/Blender.app/Contents/MacOS/Blender --version 2>/dev/null | head -1)"
else printf "  MISSING blender\n"; ok=1; fi
[ -d "/Applications/Google Chrome.app" ] && echo "  OK   chrome" || { echo "  MISSING chrome"; ok=1; }
echo "Optional (only for the local-model experiment, Phase 7):"
if ! command -v ollama >/dev/null; then echo "  --   ollama not installed"
elif ollama list >/dev/null 2>&1; then
  ollama list | grep -E "qwen3.6|gemma4" >/dev/null && echo "  OK   ollama with qwen3.6/gemma4" || echo "  --   ollama without qwen3.6 or gemma4"
else echo "  --   ollama installed but not running"; fi
exit $ok
