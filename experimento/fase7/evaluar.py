#!/usr/bin/env python3
"""Evaluador objetivo del experimento de la Fase 7: ¿el modelo hizo bien la tarea del prompt.md?

Ejecuta el `node video/render.mjs` que dejó el modelo (dos veces) y mide el resultado. No depende de CÓMO diseñó la escena (posición,
tipografía...): cuenta píxeles de cada color en instantes concretos. NO mide estética.

Uso: audio/.venv/bin/python experimento/fase7/evaluar.py <carpeta-del-experimento>   ->   escribe <carpeta>/evaluacion.json
"""
import json, pathlib, re, shutil, subprocess, sys, time
import numpy as np

D = pathlib.Path(sys.argv[1]).resolve()
FONDO, TEXTO, ACENTO = (15, 17, 21), (244, 241, 234), (255, 183, 3)
checks = []
CALIDAD_NO_PEDIDA = ("formato de color estándar yuv420p", "dos renders dan los mismos fotogramas")   # el prompt no lo exige: se puntúa aparte


def chk(nombre, ok, detalle=""):
    checks.append(dict(nombre=nombre, ok=bool(ok), detalle=str(detalle), categoria="calidad" if nombre.startswith(CALIDAD_NO_PEDIDA) else "requisito"))
    print(f"  {'OK   ' if ok else 'FALLA'} {nombre}" + (f" — {detalle}" if detalle else ""))


def sh(*a, **kw):
    return subprocess.run([str(x) for x in a], capture_output=True, text=True, **kw)


def cuenta_cerca(img, color, tol):
    return int(np.sum(np.all(np.abs(img.astype(int) - np.array(color)) <= tol, axis=2)))


def fotograma(ruta, t, ancho=960, alto=540):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(ruta), "-frames:v", "1", "-vf", f"scale={ancho}:{alto}", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], capture_output=True)
    a = np.frombuffer(r.stdout, dtype=np.uint8)
    return a.reshape(alto, ancho, 3) if a.size == ancho * alto * 3 else None


print(f"Evaluando {D.name}")
escena, render = D / "video/scene.html", D / "video/render.mjs"
chk("existe video/scene.html", escena.exists())
chk("existe video/render.mjs", render.exists())
html = escena.read_text(encoding="utf-8", errors="replace") if escena.exists() else ""
js = render.read_text(encoding="utf-8", errors="replace") if render.exists() else ""

chk("define window.DURATION = 8", re.search(r"window\.DURATION\s*=\s*8\b", html) is not None)
chk("define window.seek como función", re.search(r"window\.seek\s*=|function\s+seek|window\[['\"]seek['\"]\]", html) is not None)
chk("contiene el texto «Lámpara Arco»", "Lámpara Arco" in html)
sin_comentarios = re.sub(r"/\*.*?\*/|<!--.*?-->", "", html, flags=re.S)          # comentarios de bloque y HTML (pueden ocupar varias líneas)
sin_comentarios = re.sub(r"(?<![:\"'])//[^\n]*", "", sin_comentarios)              # comentarios de línea: SIN re.S, o '//.*' se comería todo el archivo
prohibidos = re.findall(r"\bDate\b|requestAnimationFrame|setTimeout|setInterval|Math\.random|@keyframes|animation\s*:|transition\s*:", sin_comentarios)
chk("no usa reloj, aleatoriedad ni animaciones CSS", not prohibidos, "encontrado: " + ", ".join(sorted(set(prohibidos))) if prohibidos else "")

# ---- ejecutar el render dos veces
tiempos, ok_render = [], []
for i in (1, 2):
    (D / "out").mkdir(exist_ok=True)
    destino = D / "out/titulo.mp4"
    if destino.exists(): destino.unlink()
    t0 = time.time()
    try:
        r = sh("node", "video/render.mjs", cwd=D, timeout=240)
        ok = r.returncode == 0 and destino.exists() and destino.stat().st_size > 5000
        detalle = "" if ok else (r.stderr or r.stdout)[-300:]
    except subprocess.TimeoutExpired:
        ok, detalle = False, "tiempo agotado (240 s)"
    tiempos.append(time.time() - t0); ok_render.append(ok)
    if ok: shutil.copy(destino, D / f"out/render_{i}.mp4")
    if i == 1: chk("`node video/render.mjs` termina bien y crea out/titulo.mp4", ok, f"{tiempos[0]:.1f} s" if ok else detalle)
if not ok_render[0]:
    resultado = dict(carpeta=D.name, aprobadas=sum(c["ok"] for c in checks), total=len(checks) + 9, checks=checks, render_segundos=None, nota="el render no funciona: se omiten las demás medidas")
    (D / "evaluacion.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRESULTADO: {resultado['aprobadas']}/{resultado['total']} (el render no funciona)"); sys.exit(1)

v1 = D / "out/render_1.mp4"
info = json.loads(sh("ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_read_frames,pix_fmt,duration", "-of", "json", v1).stdout)["streams"][0]
chk("vídeo H.264 1920x1080 a 30 fps", info["codec_name"] == "h264" and (info["width"], info["height"]) == (1920, 1080) and info["r_frame_rate"] == "30/1",
    f'{info["codec_name"]} {info["width"]}x{info["height"]} {info["r_frame_rate"]}')
chk("240 fotogramas (8 s)", int(info.get("nb_read_frames", 0)) == 240, f'{info.get("nb_read_frames")} fotogramas, {float(info.get("duration", 0)):.2f} s')
chk("formato de color estándar yuv420p (no yuvj420p)", info["pix_fmt"] == "yuv420p", info["pix_fmt"])

# ---- contenido: contar píxeles de cada color en instantes concretos (layout-agnóstico)
F = {t: fotograma(v1, t) for t in (0.0, 0.4, 1.0, 1.8, 2.4, 3.2, 4.0, 7.9)}
ok_frames = all(f is not None for f in F.values())
chk("se pueden extraer todos los fotogramas de muestra", ok_frames)
if ok_frames:
    total = 960 * 540
    fondo0 = cuenta_cerca(F[0.0], FONDO, 12) / total
    chk("t = 0 s: solo fondo #0f1115 (≥ 99 % de los píxeles)", fondo0 >= 0.99, f"{100 * fondo0:.2f} % de fondo")
    txt = {t: cuenta_cerca(F[t], TEXTO, 40) for t in F}
    chk("el texto aparece con fundido (nada a 0,4 s; parcial a 1,0 s; completo a 2,4 s)", txt[0.4] < 200 and txt[1.0] < txt[2.4] * 0.85 and txt[2.4] > 3000,
        f"píxeles de color texto: 0,4 s→{txt[0.4]} · 1,0 s→{txt[1.0]} · 2,4 s→{txt[2.4]}")
    lin = {t: cuenta_cerca(F[t], ACENTO, 45) for t in F}
    chk("la línea de acento crece de 1 s a 3 s (nada a 1,0 s y más y más después)", lin[1.0] < 40 and lin[1.0] < lin[1.8] < lin[2.4] < lin[3.2] * 0.97 and lin[3.2] >= 100,
        f"píxeles de acento: 1,0 s→{lin[1.0]} · 1,8→{lin[1.8]} · 2,4→{lin[2.4]} · 3,2→{lin[3.2]} · 4,0→{lin[4.0]}")
    chk("la línea termina completa y la escena queda estable (t = 4 s ≈ t = 7,9 s)", float(np.mean(np.abs(F[4.0].astype(int) - F[7.9].astype(int)))) < 2.0 and abs(lin[4.0] - lin[3.2]) <= 0.03 * max(1, lin[4.0]),
        f"diferencia media 4 s vs 7,9 s: {float(np.mean(np.abs(F[4.0].astype(int) - F[7.9].astype(int)))):.2f}")
else:
    for n in ("t = 0 s: solo fondo", "texto con fundido", "línea crece", "escena estable"): chk(n, False, "sin fotogramas")

# ---- determinismo: dos renders -> mismos fotogramas
def huella(ruta):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ruta), "-map", "0:v", "-f", "framemd5", "-"], capture_output=True, text=True)
    return [l.split(",")[-1] for l in r.stdout.splitlines() if l and not l.startswith("#")]
if ok_render[1]:
    h1, h2 = huella(D / "out/render_1.mp4"), huella(D / "out/render_2.mp4")
    iguales = sum(a == b for a, b in zip(h1, h2))
    chk("dos renders dan los mismos fotogramas (determinista)", h1 == h2 and len(h1) == 240, f"{iguales}/{len(h1)} fotogramas idénticos")
else:
    chk("dos renders dan los mismos fotogramas (determinista)", False, "el segundo render falló")

req = [c for c in checks if c["categoria"] == "requisito"]; cal = [c for c in checks if c["categoria"] == "calidad"]
aprobadas = sum(c["ok"] for c in checks)
resultado = dict(carpeta=D.name, aprobadas=aprobadas, total=len(checks), requisitos_ok=sum(c["ok"] for c in req), requisitos_total=len(req),
                 calidad_ok=sum(c["ok"] for c in cal), calidad_total=len(cal), checks=checks, render_segundos=round(sum(tiempos) / len(tiempos), 1))
(D / "evaluacion.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nRESULTADO: requisitos del prompt {resultado['requisitos_ok']}/{resultado['requisitos_total']} · calidad no pedida {resultado['calidad_ok']}/{resultado['calidad_total']} · render {resultado['render_segundos']} s")
sys.exit(0 if aprobadas == len(checks) else 1)
