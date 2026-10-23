#!/usr/bin/env python3
"""Reads a value from brief.json with a dotted path: python3 scripts/brief_get.py voice.name [--brief brief.json]  (used by the Makefile)"""
import json, pathlib, sys
args = sys.argv[1:]
path = pathlib.Path(args[args.index("--brief") + 1]) if "--brief" in args else pathlib.Path(__file__).resolve().parent.parent / "brief.json"
v = json.loads(path.read_text(encoding="utf-8"))
for k in [x for x in args if not x.startswith("--") and x != str(path)][0].split("."):
    v = v[int(k)] if isinstance(v, list) else v[k]
print(v)
