#!/usr/bin/env python3
"""Voz del promo con Kokoro-82M (mlx-audio, Apple Silicon). Fase 5.

Lee docs/guion.json (una frase por escena, con su segundo de inicio y su ventana), genera cada frase,
comprueba que cabe en su ventana (si no, la acelera lo justo) y las coloca en una pista de 20 s.

Uso:  audio/.venv/bin/python audio/narration.py [--voces ef_dora,em_alex] [--duracion 20] [--out out/audio]
Salida: out/audio/voz_<voz>.wav (mono 24 kHz, 20 s) · out/audio/<voz>/<id>.wav · out/audio/voz_<voz>.json (informe)
"""
import argparse, json, wave, pathlib, logging
import numpy as np

logging.getLogger().setLevel(logging.ERROR)
RAIZ = pathlib.Path(__file__).resolve().parent.parent
MODELO = "mlx-community/Kokoro-82M-bf16"
SR = 24000
MARGEN = 0.15          # segundos que se dejan libres al final de cada ventana
VEL_MAX = 1.30         # no se acelera más: la voz se vuelve poco natural


def guardar_wav(ruta, audio, sr):
    pcm = np.clip(audio, -1.0, 1.0)
    pcm = (pcm * 32767).astype("<i2")
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


def recortar_silencio(a, umbral=0.004, cola=0.05):
    """Quita el silencio inicial y final de una frase (deja `cola` s) para que 'inicio' signifique 'empieza a hablar'."""
    idx = np.where(np.abs(a) > umbral)[0]
    if idx.size == 0:
        return a
    i0 = max(0, idx[0] - int(0.02 * SR)); i1 = min(a.size, idx[-1] + int(cola * SR))
    return a[i0:i1]


def generar(modelo, texto, voz, velocidad):
    trozos = [np.array(r.audio, dtype=np.float32) for r in modelo.generate(text=texto, voice=voz, speed=velocidad, lang_code="e")]
    return recortar_silencio(np.concatenate(trozos))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voces", default="ef_dora,em_alex")
    ap.add_argument("--duracion", type=float, default=20.0)
    ap.add_argument("--out", default="out/audio")
    a = ap.parse_args()
    from mlx_audio.tts.utils import load_model
    modelo = load_model(MODELO)
    guion = json.loads((RAIZ / "docs/guion.json").read_text(encoding="utf-8"))["segmentos"]
    salida = RAIZ / a.out
    salida.mkdir(parents=True, exist_ok=True)
    codigo = 0

    for voz in a.voces.split(","):
        (salida / voz).mkdir(exist_ok=True)
        pista = np.zeros(int(a.duracion * SR), dtype=np.float32)
        informe = []
        for s in guion:
            vel = 1.0
            audio = generar(modelo, s["texto"], voz, vel)
            dur = audio.size / SR
            while dur > s["ventana"] - MARGEN and vel < VEL_MAX:       # no cabe: se acelera de 5 en 5 %
                vel = round(vel + 0.05, 2)
                audio = generar(modelo, s["texto"], voz, vel)
                dur = audio.size / SR
            cabe = dur <= s["ventana"] - MARGEN + 1e-9
            fin = s["inicio"] + dur
            if not cabe or fin > a.duracion:
                codigo = 1
            i0 = int(s["inicio"] * SR)
            pista[i0:i0 + audio.size] += audio[: max(0, pista.size - i0)]
            guardar_wav(salida / voz / f"{s['id']}.wav", audio, SR)
            informe.append(dict(id=s["id"], inicio=s["inicio"], fin=round(fin, 2), duracion=round(dur, 2), ventana=s["ventana"],
                                velocidad=vel, cabe=cabe, pico=round(float(np.max(np.abs(audio))), 3)))
        pico = float(np.max(np.abs(pista)))
        if pico > 0.98:
            pista *= 0.98 / pico                                      # evita recortes al sumar
        guardar_wav(salida / f"voz_{voz}.wav", pista, SR)
        (salida / f"voz_{voz}.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n== {voz} ==")
        for r in informe:
            print(f"  {r['id']:<14} {r['inicio']:>5.1f}→{r['fin']:>5.2f} s  dur {r['duracion']:.2f} / ventana {r['ventana']:.1f}  vel {r['velocidad']:.2f}  {'OK' if r['cabe'] else 'NO CABE'}")
    raise SystemExit(codigo)


if __name__ == "__main__":
    main()
