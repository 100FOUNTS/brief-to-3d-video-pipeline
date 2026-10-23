#!/usr/bin/env bash
# Comprueba que el entorno de la Fase 0 está listo.
ok=0
check() {
  local name="$1"; shift
  if out=$("$@" 2>&1 | head -1); then printf "  OK   %-10s %s\n" "$name" "$out"; else printf "  FALTA %-9s\n" "$name"; ok=1; fi
}
echo "Herramientas:"
check node node --version
check npm npm --version
check ffmpeg bash -c 'ffmpeg -version | head -1'
check python3 python3 --version
check uv uv --version
check claude claude --version
check git git --version
if [ -x /Applications/Blender.app/Contents/MacOS/Blender ]; then
  printf "  OK   %-10s %s\n" blender "$(/Applications/Blender.app/Contents/MacOS/Blender --version 2>/dev/null | head -1)"
else printf "  FALTA blender\n"; ok=1; fi
[ -d "/Applications/Google Chrome.app" ] && echo "  OK   chrome" || { echo "  FALTA chrome"; ok=1; }
echo "Opcional (solo para el experimento con un modelo local, Fase 7):"
if ! command -v ollama >/dev/null; then echo "  --   ollama no instalado"
elif ollama list >/dev/null 2>&1; then
  ollama list | grep -E "qwen3.6|gemma4" >/dev/null && echo "  OK   ollama con qwen3.6/gemma4" || echo "  --   ollama sin qwen3.6 ni gemma4"
else echo "  --   ollama instalado pero no está en marcha"; fi
exit $ok
