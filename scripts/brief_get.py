#!/usr/bin/env python3
"""Lee un valor de brief.json con ruta de puntos: python3 scripts/brief_get.py voz.nombre [--brief brief.json]  (lo usa el Makefile)"""
import json, pathlib, sys
args = sys.argv[1:]
ruta = pathlib.Path(args[args.index("--brief") + 1]) if "--brief" in args else pathlib.Path(__file__).resolve().parent.parent / "brief.json"
v = json.loads(ruta.read_text(encoding="utf-8"))
for k in [x for x in args if not x.startswith("--") and x != str(ruta)][0].split("."):
    v = v[int(k)] if isinstance(v, list) else v[k]
print(v)
