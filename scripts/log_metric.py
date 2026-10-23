#!/usr/bin/env python3
"""Appends ONE row to docs/metrics.csv with correct quoting (notes and model names may contain commas).
Usage: python3 scripts/log_metric.py <phase> "<model>" <minutes> <attempts> <result> "<notes>" [--date 2026-10-15]
NOTE: the minutes are ESTIMATES from the session (not all were timed); the attempts are the number of versions until it was accepted."""
import csv, datetime, pathlib, sys
if len(sys.argv) < 7:
    sys.exit(__doc__)
phase, model, minutes, attempts, result, notes = sys.argv[1:7]
date = sys.argv[sys.argv.index("--date") + 1] if "--date" in sys.argv else datetime.date.today().isoformat()
float(minutes); int(attempts)                                   # fails if they are not numbers
path = pathlib.Path(__file__).resolve().parent.parent / "docs/metrics.csv"
with path.open("a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow([date, phase, model, minutes, attempts, result, notes])
print(f"logged: phase {phase} · {model} · {minutes} min · {attempts} attempts · {result}")
