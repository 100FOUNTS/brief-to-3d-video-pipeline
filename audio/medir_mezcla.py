#!/usr/bin/env python3
"""Mide, en cada ventana de habla, cuánto más fuerte suena la voz que la música ya 'ducked' (LU). Usa los mismos filtros que mix.sh.
Regla práctica para narración sobre música: voz >= ~10 LU por encima de la música. Uso: audio/.venv/bin/python audio/medir_mezcla.py [voz]"""
import json, math, re, subprocess, sys, pathlib
PESO_VOZ = 1.7      # el mismo peso que usa audio/mix.sh en amix (la voz entra 1,7 veces más fuerte que la música)
GANANCIA_VOZ_DB = 20 * math.log10(PESO_VOZ)
RAIZ = pathlib.Path(__file__).resolve().parent.parent
voz = sys.argv[1] if len(sys.argv) > 1 else "ef_dora"
tmp = RAIZ / "out/audio/tmp"; tmp.mkdir(parents=True, exist_ok=True)
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", RAIZ / "out/audio/musica.wav", "-i", RAIZ / f"out/audio/voz_{voz}.wav", "-filter_complex",
    "[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,asplit=2[vsc][v2];[0:a]volume=-2dB[m];[m][vsc]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=450:makeup=1[mduck]",
    "-map", "[mduck]", tmp / "musica_duck.wav", "-map", "[v2]", tmp / "voz.wav"], check=True)
def lufs(archivo, a, b):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", str(a), "-t", str(b - a), "-i", archivo, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return float(m[-1]) if m else float("-inf")
seg = json.loads((RAIZ / f"out/audio/voz_{voz}.json").read_text())
print(f"Voz {voz}: nivel de la voz y de la música dentro de cada ventana de habla")
peor = 99
for s in seg:
    a, b = s["inicio"] + 0.1, s["fin"] - 0.05
    if b - a < 0.4:                                       # ebur128 necesita >= 0,4 s: con menos devuelve -65 LUFS (basura)
        print(f"  {s['id']:<14} ventana de {b - a:.2f} s: demasiado corta para medir el volumen (se omite)")
        continue
    v, m = lufs(tmp / "voz.wav", a, b), lufs(tmp / "musica_duck.wav", a, b)
    dif = v + GANANCIA_VOZ_DB - m                       # diferencia real en la mezcla, con el peso de la voz
    peor = min(peor, dif)
    print(f"  {s['id']:<14} voz {v + GANANCIA_VOZ_DB:6.1f}  música {m:6.1f}   diferencia {dif:+5.1f} LU")
sin_duck = lufs(RAIZ / "out/audio/musica.wav", 5.6, 7.7)
duck = lufs(tmp / "musica_duck.wav", 5.6, 7.7)
print(f"Efecto del ducking en 5,6–7,7 s: música {sin_duck:.1f} → {duck:.1f} LUFS ({duck - sin_duck:+.1f} LU)")
print(f"PEOR diferencia voz–música: {peor:+.1f} LU")
