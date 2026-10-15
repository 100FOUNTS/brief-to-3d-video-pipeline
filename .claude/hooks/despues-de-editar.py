#!/usr/bin/env python3
"""Hook PostToolUse (Write|Edit) de este proyecto. Si algo falla sale con 2 y Claude ve el mensaje.

  - Si se edita brief.json: lo valida y regenera lo que depende de él (scripts/generar_desde_brief.py).
  - Si se edita otro brief (brief.frio.json...): solo lo VALIDA (no toca los archivos del proyecto principal).
  - Si se edita la plantilla de HyperFrames: regenera index.html y ejecuta `npx hyperframes lint` sobre el resultado.
"""
import json, os, pathlib, re, subprocess, sys

datos = json.load(sys.stdin)
ruta = (datos.get("tool_input") or {}).get("file_path")
if not ruta:
    sys.exit(0)
proyecto = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or datos.get("cwd") or ".").resolve()
try:
    rel = pathlib.Path(ruta).expanduser().resolve().relative_to(proyecto).as_posix()
except ValueError:
    sys.exit(0)


def ejecutar(cmd, cwd, etiqueta):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[{etiqueta}] FALLÓ (código {r.returncode}):\n{(r.stdout + r.stderr).strip()[-1500:]}", file=sys.stderr)
        sys.exit(2)
    return r.stdout


if rel == "brief.json":
    out = ejecutar(["python3", "scripts/generar_desde_brief.py", "--brief", rel], proyecto, "generar desde el brief")
    print(out.strip())
elif re.fullmatch(r"brief[^/]*\.json", rel):
    # brief de una variante: solo se valida; regenerarlo aquí pisaría los archivos del proyecto principal con los de la variante
    print(ejecutar(["python3", "scripts/generar_desde_brief.py", "--brief", rel, "--validar"], proyecto, "validar el brief").strip())
elif rel == "plantillas/hyperframes-promo.template.html":
    ejecutar(["python3", "scripts/generar_desde_brief.py", "--brief", "brief.json"], proyecto, "generar desde la plantilla")
    out = ejecutar(["npx", "hyperframes", "lint"], proyecto / "hyperframes/promo", "hyperframes lint")
    print("plantilla regenerada; " + out.strip().splitlines()[-1] if out.strip() else "plantilla regenerada; lint sin salida")
sys.exit(0)
