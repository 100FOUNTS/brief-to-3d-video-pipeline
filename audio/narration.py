#!/usr/bin/env python3
"""Voz del promo con Kokoro-82M (mlx-audio, Apple Silicon). Fase 5.

Lee docs/guion.json (una frase por escena, con su segundo de inicio y su ventana), genera cada frase,
comprueba que cabe en su ventana (si no, la acelera lo justo) y las coloca en una pista de 20 s.

Uso:  audio/.venv/bin/python audio/narration.py [--motor kokoro|qwen3] [--voces ef_dora,em_alex] [--instruct "..."] [--duracion 20] [--out out/audio]
Motores: kokoro (Kokoro-82M, 0,39 GB) · qwen3 (Qwen3-TTS 1.7B CustomVoice 8 bits, 3,08 GB; hablantes predefinidos en español forzado)
Salida: out/audio/voz_<etiqueta>.wav (mono, 20 s) · out/audio/<etiqueta>/<id>.wav · out/audio/voz_<etiqueta>.json (informe)
  etiqueta = la voz (kokoro) o "<motor>-<voz>" (otros motores), para no pisar las de Kokoro.
"""
import argparse, json, wave, pathlib, logging, re, subprocess, tempfile, unicodedata
import numpy as np

logging.getLogger().setLevel(logging.ERROR)
RAIZ = pathlib.Path(__file__).resolve().parent.parent
MOTORES = {
    "kokoro": dict(modelo="mlx-community/Kokoro-82M-bf16", lang="e", voces="ef_dora,em_alex"),
    # qwen3 ignora 'speed' y su ritmo varía mucho entre semillas (la misma frase: 5 a 9,6 s): se generan varias candidatas,
    # se escoge la más corta que Whisper confirme correcta y solo entonces se acelera con ffmpeg.
    "qwen3": dict(modelo="mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit", lang="spanish", voces="ryan,aiden",
                  sin_velocidad=True, candidatas=5,
                  instruct="Speak at a brisk, natural narration pace. Do not drag words or pause for long."),
}
STT_MODELO = "mlx-community/whisper-large-v3-asr-fp16"
ATEMPO_MAX = 1.25      # máxima aceleración posterior con ffmpeg (sin cambiar el tono)
SR = 24000             # se sobrescribe con la frecuencia real del modelo
SEMILLA = 0            # semilla fija: la voz se regenera idéntica (qwen3 usa sus propias semillas por candidata)
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


def generar(modelo, texto, voz, velocidad, lang, instruct=None, sin_velocidad=False):
    import mlx.core as mx
    if not sin_velocidad:
        mx.random.seed(SEMILLA)                       # Kokoro usa ruido aleatorio interno: sin semilla fija cada ejecución da una forma de onda distinta
    kw = dict(text=texto, voice=voz, lang_code=lang)
    if not sin_velocidad:
        kw["speed"] = velocidad
    if instruct:
        kw["instruct"] = instruct
    trozos = [np.array(r.audio, dtype=np.float32) for r in modelo.generate(**kw)]
    return recortar_silencio(np.concatenate(trozos))


def normalizar(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-zñ0-9]+", t)


def errores(ref, hip):
    """Distancia de edición entre listas de palabras (sustituciones + borrados + inserciones)."""
    d = list(range(len(hip) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hip, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
    return d[len(hip)]


def transcribir(stt, audio):
    with tempfile.TemporaryDirectory() as td:
        ruta = pathlib.Path(td) / "c.wav"
        guardar_wav(ruta, audio, SR)
        r = stt.generate(str(ruta), language="es")
        return getattr(r, "text", str(r)).strip()


def acelerar(audio, factor):
    """Acelera sin cambiar el tono con el filtro atempo de ffmpeg."""
    with tempfile.TemporaryDirectory() as td:
        a, b = pathlib.Path(td) / "a.wav", pathlib.Path(td) / "b.wav"
        guardar_wav(a, audio, SR)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(a), "-filter:a", f"atempo={factor}", str(b)], check=True)
        with wave.open(str(b)) as w:
            return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768


def mejor_candidata(modelo, stt, texto, voz, cfg, instruct, extra_ventana_ok):
    """Genera N candidatas con semillas fijas y devuelve la más corta cuyo texto Whisper confirma (o la de menos errores)."""
    import mlx.core as mx
    ref = normalizar(texto)
    cands = []
    for k in range(cfg["candidatas"]):
        mx.random.seed(k)
        a = generar(modelo, texto, voz, 1.0, cfg["lang"], instruct, sin_velocidad=True)
        cands.append(dict(semilla=k, audio=a, dur=a.size / SR))
    for c in sorted(cands, key=lambda c: c["dur"]):
        c["oido"] = transcribir(stt, c["audio"])
        c["err"] = errores(ref, normalizar(c["oido"]))
        if c["err"] == 0:
            return c, cands
    return min(cands, key=lambda c: (c.get("err", 99), c["dur"])), cands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--motor", default=None, choices=list(MOTORES))
    ap.add_argument("--brief", default="", help="brief.json: voz.motor y voz.nombre (si no se pasan --motor/--voces)")
    ap.add_argument("--voces", default=None)
    ap.add_argument("--instruct", default=None, help="instrucción de estilo (solo motores que la admiten, p. ej. qwen3)")
    ap.add_argument("--extra-ventana", type=float, default=0.0, help="segundos que se amplía cada ventana (para voces más lentas que el guion)")
    ap.add_argument("--duracion", type=float, default=20.0)
    ap.add_argument("--out", default="out/audio")
    a = ap.parse_args()
    from mlx_audio.tts.utils import load_model
    global SR
    if a.brief:
        bv = json.loads((RAIZ / a.brief if not pathlib.Path(a.brief).is_absolute() else pathlib.Path(a.brief)).read_text(encoding="utf-8"))["voz"]
        a.motor = a.motor or bv["motor"]
        a.voces = a.voces or bv["nombre"]
    a.motor = a.motor or "kokoro"
    cfg = MOTORES[a.motor]
    modelo = load_model(cfg["modelo"])
    SR = int(getattr(modelo, "sample_rate", SR))
    voces = (a.voces or cfg["voces"]).split(",")
    instruct = a.instruct if a.instruct is not None else cfg.get("instruct")
    stt = None
    if cfg.get("sin_velocidad"):
        from mlx_audio.stt.utils import load_model as load_stt
        stt = load_stt(STT_MODELO)
    guion = json.loads((RAIZ / "docs/guion.json").read_text(encoding="utf-8"))["segmentos"]
    salida = RAIZ / a.out
    salida.mkdir(parents=True, exist_ok=True)
    codigo = 0

    for voz in voces:
        etq = voz if a.motor == "kokoro" else f"{a.motor}-{voz}"
        (salida / etq).mkdir(exist_ok=True)
        pista = np.zeros(int(a.duracion * SR), dtype=np.float32)
        informe = []
        for s in guion:
            vel = 1.0
            ventana = s["ventana"] + a.extra_ventana
            extra = {}
            if cfg.get("sin_velocidad"):
                c, todas = mejor_candidata(modelo, stt, s["texto"], voz, cfg, instruct, True)
                audio, dur = c["audio"], c["dur"]
                extra = dict(semilla=c["semilla"], oido=c["oido"], errores_palabras=c["err"], candidatas=[round(x["dur"], 2) for x in todas])
                if dur > ventana - MARGEN:                               # no cabe: se acelera con ffmpeg lo justo
                    vel = min(ATEMPO_MAX, round(dur / (ventana - MARGEN) + 0.02, 2))
                    audio = acelerar(audio, vel)
                    dur = audio.size / SR
            else:
                audio = generar(modelo, s["texto"], voz, vel, cfg["lang"], instruct)
                dur = audio.size / SR
                while dur > ventana - MARGEN and vel < VEL_MAX:         # no cabe: se acelera de 5 en 5 %
                    vel = round(vel + 0.05, 2)
                    audio = generar(modelo, s["texto"], voz, vel, cfg["lang"], instruct)
                    dur = audio.size / SR
            cabe = dur <= ventana - MARGEN + 1e-9
            fin = s["inicio"] + dur
            if not cabe or fin > a.duracion:
                codigo = 1
            i0 = int(s["inicio"] * SR)
            pista[i0:i0 + audio.size] += audio[: max(0, pista.size - i0)]
            guardar_wav(salida / etq / f"{s['id']}.wav", audio, SR)
            informe.append(dict(id=s["id"], inicio=s["inicio"], fin=round(fin, 2), duracion=round(dur, 2), ventana=ventana,
                                velocidad=vel, cabe=cabe, pico=round(float(np.max(np.abs(audio))), 3), **extra))
        pico = float(np.max(np.abs(pista)))
        if pico > 0.98:
            pista *= 0.98 / pico                                      # evita recortes al sumar
        guardar_wav(salida / f"voz_{etq}.wav", pista, SR)
        (salida / f"voz_{etq}.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n== {a.motor} · {voz} ==")
        for r in informe:
            print(f"  {r['id']:<14} {r['inicio']:>5.1f}→{r['fin']:>5.2f} s  dur {r['duracion']:.2f} / ventana {r['ventana']:.1f}  vel {r['velocidad']:.2f}  {'OK' if r['cabe'] else 'NO CABE'}"
                  + (f"  [candidatas {r['candidatas']} → semilla {r['semilla']}, errores {r['errores_palabras']}]" if 'semilla' in r else ""))
    raise SystemExit(codigo)


if __name__ == "__main__":
    main()
