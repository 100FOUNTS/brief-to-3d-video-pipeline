#!/usr/bin/env python3
"""Comprueba que la voz se entiende: la transcribe con Whisper (local, mlx-audio) y calcula el WER frente a docs/guion.json.
WER = (sustituciones + borrados + inserciones) / palabras del guion. 0 % = idéntico. Es una medida de inteligibilidad,
NO de naturalidad: si la voz suena agradable solo se puede juzgar escuchándola.
Uso: audio/.venv/bin/python audio/verificar_voz.py out/audio/voz_ef_dora.wav [...]"""
import json, os, re, sys, subprocess, pathlib, unicodedata
RAIZ = pathlib.Path(__file__).resolve().parent.parent
MODELO = os.environ.get("WHISPER_MODELO", "mlx-community/whisper-large-v3-asr-fp16")   # modelo grande completo (3 GB); se cambia con WHISPER_MODELO

def normalizar(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")          # sin tildes: el reconocedor las pone a su manera
    return re.findall(r"[a-zñ0-9]+", t)

def distancias(ref, hip):
    d = list(range(len(hip) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hip, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
    return d

def wer(ref, hip):
    """WER completo: cuenta también lo que el reconocedor invente de más."""
    return distancias(ref, hip)[len(hip)] / max(1, len(ref))

def wer_sin_cola(ref, hip):
    """WER sin penalizar texto inventado DESPUÉS de terminar el guion (Whisper alucina en los silencios finales)."""
    return min(distancias(ref, hip)) / max(1, len(ref))

guion = " ".join(s["texto"] for s in json.loads((RAIZ / "docs/guion.json").read_text(encoding="utf-8"))["segmentos"])
ref = normalizar(guion)
for ruta in sys.argv[1:]:
    p = pathlib.Path(ruta)
    base = RAIZ / "out/audio/transcripcion" / p.stem
    base.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, "-m", "mlx_audio.stt.generate", "--model", MODELO, "--audio", str(p), "--output-path", str(base), "--format", "txt", "--language", "es"],
                   capture_output=True, text=True)
    if not list(base.parent.glob(p.stem + '*')):
        sys.exit('El reconocedor falló:\n' + (r.stderr or '')[-800:])
    cand = sorted(base.parent.glob(p.stem + "*.txt")) or sorted(base.parent.glob("*.txt"))
    texto = cand[-1].read_text(encoding="utf-8").strip() if cand else ""
    hip = normalizar(texto)
    print(f"\n{p.name}\n  guion     : {guion}\n  oído      : {texto}\n  WER completo   : {100 * wer(ref, hip):.1f} %\n  WER sin la cola inventada: {100 * wer_sin_cola(ref, hip):.1f} %   ({len(ref)} palabras del guion)")
