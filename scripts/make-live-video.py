#!/usr/bin/env python3
"""Assembles the live-process video (Phase 4b) from out/blender/live/report.txt and step_N.png.
The captions come LITERALLY from the 'STEP|n|object|value|observation' lines of the session report.
(The captions and the report are in Spanish: they are the content of that session, kept as it was recorded.)"""
import json, re, subprocess, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
report = (root / "out/blender/live/report.txt").read_text(encoding="utf-8")
steps = []
for line in report.splitlines():
    if line.startswith("PASO|"):                                  # marker written by the recorded Spanish session
        _, n, obj, value, obs = (x.strip() for x in line.split("|", 4))
        steps.append(dict(n=int(n), object=obj, value=value, obs=obs, image=f"../out/blender/live/step_{n}.png"))
if not steps: sys.exit("There are no PASO| lines in the report")
for p in steps:
    assert (root / "out/blender/live" / f"step_{p['n']}.png").exists(), f"step_{p['n']}.png is missing"
# conclusion: the paragraph after the PASO lines (as the session wrote it), trimmed to the essentials
rest = [l.strip() for l in report.splitlines() if l.strip() and not l.startswith("PASO|")]
conclusion = rest[0] if rest else ""
# The video must not be more optimistic than the report: the sentences where the session admits its failures are appended verbatim.
sentences = [f.strip() for l in rest[1:] for f in re.split(r"(?<=[.!?])\s+", l)]
admitted = [f for f in sentences if re.search(r"no ayudaron|retroceso", f)]
if admitted:
    conclusion = conclusion + " " + " ".join(admitted)
data = dict(
    title="Un asistente maneja Blender en vivo",
    subtitle="Mira la escena, cambia una sola luz y vuelve a mirar. Estas son las imágenes reales de esa sesión.",
    closing_title="Mejor que el inicio, no del todo equilibrado",
    closing_text=conclusion,
    steps=steps,
)
template = (root / "video/live-process.template.html").read_text(encoding="utf-8")
(root / "video/live-process.html").write_text(template.replace("/*DATA*/", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
subprocess.run(["node", "video/render.mjs", "video/live-process.html", "out/live-process-mcp.mp4"], cwd=root, check=True)
