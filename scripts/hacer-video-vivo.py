#!/usr/bin/env python3
"""Monta el vídeo del proceso en vivo (Fase 4b) a partir de out/blender/vivo/informe.txt y paso_N.png.
Los rótulos salen LITERALMENTE de las líneas 'PASO|n|objeto|valor|observación' del informe de la sesión."""
import json, re, subprocess, sys, pathlib
raiz = pathlib.Path(__file__).resolve().parent.parent
informe = (raiz / "out/blender/vivo/informe.txt").read_text(encoding="utf-8")
pasos = []
for linea in informe.splitlines():
    if linea.startswith("PASO|"):
        _, n, objeto, valor, obs = (x.strip() for x in linea.split("|", 4))
        pasos.append(dict(n=int(n), objeto=objeto, valor=valor, obs=obs, imagen=f"../out/blender/vivo/paso_{n}.png"))
if not pasos: sys.exit("No hay líneas PASO| en el informe")
for p in pasos:
    assert (raiz / "out/blender/vivo" / f"paso_{p['n']}.png").exists(), f"falta paso_{p['n']}.png"
# conclusión: el párrafo que sigue a las líneas PASO (tal cual lo escribió la sesión), recortado a lo esencial
resto = [l.strip() for l in informe.splitlines() if l.strip() and not l.startswith("PASO|")]
conclusion = resto[0] if resto else ""
# El vídeo no debe quedar más optimista que el informe: se añaden, literales, las frases donde la sesión admite sus fallos.
frases = [f.strip() for l in resto[1:] for f in re.split(r"(?<=[.!?])\s+", l)]
admitidas = [f for f in frases if re.search(r"no ayudaron|retroceso", f)]
if admitidas:
    conclusion = conclusion + " " + " ".join(admitidas)
datos = dict(
    titulo="Un asistente maneja Blender en vivo",
    subtitulo="Mira la escena, cambia una sola luz y vuelve a mirar. Estas son las imágenes reales de esa sesión.",
    cierre_titulo="Mejor que el inicio, no del todo equilibrado",
    cierre_texto=conclusion,
    pasos=pasos,
)
plantilla = (raiz / "video/proceso-vivo.template.html").read_text(encoding="utf-8")
(raiz / "video/proceso-vivo.html").write_text(plantilla.replace("/*DATOS*/", json.dumps(datos, ensure_ascii=False)), encoding="utf-8")
subprocess.run(["node", "video/render.mjs", "video/proceso-vivo.html", "out/proceso-vivo-mcp.mp4"], cwd=raiz, check=True)
