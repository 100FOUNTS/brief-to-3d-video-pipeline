#!/usr/bin/env python3
"""Añade UNA fila a docs/metricas.csv con el entrecomillado correcto (las notas y los nombres de modelo pueden llevar comas).
Uso: python3 scripts/registrar_metrica.py <fase> "<modelo>" <minutos> <intentos> <resultado> "<notas>" [--fecha 2026-10-15]
NOTA: los minutos son ESTIMACIONES de la sesión (no se cronometraron todos); los intentos, el número de versiones hasta darlo por bueno."""
import csv, datetime, pathlib, sys
if len(sys.argv) < 7:
    sys.exit(__doc__)
fase, modelo, minutos, intentos, resultado, notas = sys.argv[1:7]
fecha = sys.argv[sys.argv.index("--fecha") + 1] if "--fecha" in sys.argv else datetime.date.today().isoformat()
float(minutos); int(intentos)                                   # falla si no son números
ruta = pathlib.Path(__file__).resolve().parent.parent / "docs/metricas.csv"
with ruta.open("a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow([fecha, fase, modelo, minutos, intentos, resultado, notas])
print(f"registrada: fase {fase} · {modelo} · {minutos} min · {intentos} intentos · {resultado}")
