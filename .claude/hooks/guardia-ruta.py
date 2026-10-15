#!/usr/bin/env python3
"""Hook PreToolUse (Write|Edit) de este proyecto. Con exit 2 BLOQUEA la edición y le devuelve el motivo a Claude.

Bloquea:
  1. escribir fuera de la carpeta del proyecto (excepto el scratchpad temporal de Claude Code, /private/tmp/claude-* y /tmp/claude-*)
  2. editar a mano archivos GENERADOS desde brief.json (se perderían en el siguiente `make generar`)
"""
import json, os, pathlib, sys

GENERADOS = {
    "hyperframes/promo/index.html": "se genera desde plantillas/hyperframes-promo.template.html y brief.json",
    "docs/guion.json": "se genera desde brief.json (voz.apertura, beneficios[].voz, voz.cierre)",
    "viewer/src/brief.generated.js": "se genera desde brief.json (producto y paleta)",
}
TEMPORALES = ("/private/tmp/claude-", "/tmp/claude-")


def bloquear(motivo):
    print(f"BLOQUEADO por el hook guardia-ruta: {motivo}", file=sys.stderr)
    sys.exit(2)


datos = json.load(sys.stdin)
ruta = (datos.get("tool_input") or {}).get("file_path")
if not ruta:
    sys.exit(0)
proyecto = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or datos.get("cwd") or ".").resolve()
destino = pathlib.Path(ruta).expanduser().resolve()
if str(destino).startswith(TEMPORALES):
    sys.exit(0)
try:
    rel = destino.relative_to(proyecto).as_posix()
except ValueError:
    bloquear(f"{destino} está FUERA de la carpeta del proyecto ({proyecto}). Este proyecto solo escribe dentro de su carpeta.")
if rel in GENERADOS:
    bloquear(f"{rel} es un archivo GENERADO ({GENERADOS[rel]}). Edita brief.json o la plantilla y ejecuta `make generar`; si lo editas aquí se perderá.")
sys.exit(0)
