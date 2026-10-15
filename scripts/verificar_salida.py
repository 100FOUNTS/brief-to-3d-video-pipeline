#!/usr/bin/env python3
"""Comprobaciones automáticas de la salida de `make studio` (Fase 6). Sale con 1 si alguna falla.

Cubre lo que cada pieza por separado no ve: que el vídeo FINAL tenga imagen y audio, que mida lo que debe, que el volumen sea
el pactado, que el color de fondo del vídeo sea el del brief, que haya voz en cada ventana y que el .glb traiga las 7 piezas.
NO mide si la voz suena natural ni si el diseño es bonito: eso se juzga mirando y escuchando.

Uso: audio/.venv/bin/python scripts/verificar_salida.py [--brief brief.json]
"""
import argparse, json, pathlib, re, struct, subprocess, sys, wave
import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PIEZAS = ["base", "brazo-inferior", "articulacion-inferior", "brazo-superior", "articulacion-superior", "pantalla", "bombilla"]
resultados = []


def chk(nombre, ok, detalle=""):
    resultados.append(bool(ok))
    print(f"  {'OK   ' if ok else 'FALLA'} {nombre}" + (f" — {detalle}" if detalle else ""))


def sh(*args):
    return subprocess.run([str(a) for a in args], capture_output=True, text=True)


def fotograma(ruta, t, ancho, alto, formato):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(ruta), "-frames:v", "1", "-vf", f"scale={ancho}:{alto}", "-pix_fmt", formato, "-f", "rawvideo", "-"], capture_output=True)
    return np.frombuffer(r.stdout, dtype=np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", default="brief.json")
    a = ap.parse_args()
    brief = json.loads((RAIZ / a.brief).read_text(encoding="utf-8"))
    voz = brief["voz"]
    etq = voz["nombre"] if voz["motor"] == "kokoro" else f'{voz["motor"]}-{voz["nombre"]}'
    final = RAIZ / "out/promo-final.mp4"
    print(f"Verificando la salida de '{brief['producto']['nombre']}' ({a.brief})")

    print("\nArchivos")
    for rel, minimo in [("out/promo-final.mp4", 100_000), ("out/lampara.glb", 10_000), ("viewer/dist/index.html", 200), (f"out/audio/mezcla_{etq}.wav", 100_000), ("out/promo-hyperframes.mp4", 100_000)]:
        p = RAIZ / rel
        chk(rel, p.exists() and p.stat().st_size >= minimo, f"{p.stat().st_size / 1e6:.2f} MB" if p.exists() else "no existe")
    if not final.exists():
        sys.exit(1)

    print("\nVídeo final")
    info = json.loads(sh("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", final).stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), {})
    chk("vídeo H.264 1920x1080 a 30 fps", v.get("codec_name") == "h264" and (v.get("width"), v.get("height")) == (1920, 1080) and v.get("r_frame_rate") == "30/1",
        f'{v.get("codec_name")} {v.get("width")}x{v.get("height")} {v.get("r_frame_rate")}')
    dur_v = float(v.get("duration", 0)); dur_a = float(au.get("duration", 0))
    chk("duración 20,0 s (±0,1)", abs(dur_v - brief["video"]["duracion"]) <= 0.1, f"{dur_v:.2f} s")
    chk("tiene pista de audio AAC a 48 kHz", au.get("codec_name") == "aac" and au.get("sample_rate") == "48000", f'{au.get("codec_name")} {au.get("sample_rate")} Hz')
    chk("audio y vídeo duran lo mismo (±0,15 s)", abs(dur_v - dur_a) <= 0.15, f"vídeo {dur_v:.2f} s · audio {dur_a:.2f} s")

    print("\nAudio")
    r = sh("ffmpeg", "-hide_banner", "-nostats", "-i", final, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-")
    integrado = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr); pico = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    li, lp = (float(integrado[-1]) if integrado else None), (float(pico[-1]) if pico else None)
    chk("volumen integrado -16 LUFS (±1)", li is not None and abs(li + 16) <= 1, f"{li} LUFS")
    chk("pico real <= -1,0 dBFS (sin recortes)", lp is not None and lp <= -1.0, f"{lp} dBFS")
    # voz presente en cada ventana del guion
    guion = json.loads((RAIZ / "docs/guion.json").read_text(encoding="utf-8"))["segmentos"]
    with wave.open(str(RAIZ / f"out/audio/voz_{etq}.wav")) as w:
        sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
    informe = json.loads((RAIZ / f"out/audio/voz_{etq}.json").read_text(encoding="utf-8"))
    for s, inf in zip(guion, informe):
        tramo = x[int(s["inicio"] * sr): int((s["inicio"] + inf["duracion"]) * sr)]
        rms = float(np.sqrt(np.mean(tramo ** 2))) if tramo.size else 0
        chk(f"voz presente en '{s['id']}' ({s['inicio']:.1f}–{inf['fin']:.1f} s) y cabe en su ventana", rms > 0.02 and inf["cabe"], f"RMS {rms:.3f}, {inf['duracion']:.2f}/{inf['ventana']:.1f} s")

    print("\nImagen")
    tiempos = [1, 3.5, 6, 10, 14, 18.5]
    gris = [fotograma(final, t, 32, 18, "gray").astype(np.float32) for t in tiempos]
    chk("ningún fotograma de muestra está vacío", all(g.size == 32 * 18 for g in gris), "ffmpeg devolvió imagen en las 6 muestras")
    cambios = [float(np.mean(np.abs(gris[i] - gris[i + 1]))) for i in range(len(gris) - 1)]
    chk("el vídeo cambia a lo largo del tiempo (no está congelado)", sum(c > 2 for c in cambios) >= 4, "diferencia entre muestras: " + ", ".join(f"{c:.1f}" for c in cambios))
    rgb = fotograma(final, 10, 64, 36, "rgb24").reshape(36, 64, 3).astype(int)
    esquina = rgb[1, 1]
    objetivo = np.array([int(brief["paleta"]["fondo"][i:i + 2], 16) for i in (1, 3, 5)])
    chk("el color de fondo del vídeo es el del brief (±14 por canal)", np.all(np.abs(esquina - objetivo) <= 14), f"vídeo {tuple(int(c) for c in esquina)} · brief {tuple(int(c) for c in objetivo)} ({brief['paleta']['fondo']})")

    print("\nModelo 3D (.glb)")
    d = (RAIZ / "out/lampara.glb").read_bytes()
    n = struct.unpack("<I", d[12:16])[0]
    nodos = [x["name"] for x in json.loads(d[20:20 + n])["nodes"]]
    faltan = [p for p in PIEZAS if p not in nodos]
    chk("trae las 7 piezas con su nombre", not faltan, "faltan: " + ", ".join(faltan) if faltan else f"{len(nodos)} nodos")

    ok = all(resultados)
    print(f"\n{'TODO CORRECTO' if ok else 'HAY FALLOS'}: {sum(resultados)}/{len(resultados)} comprobaciones")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
