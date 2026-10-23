#!/usr/bin/env python3
"""Objective evaluator of the Phase 7 experiment: did the model do the task in prompt.md correctly?

Runs the `node video/render.mjs` that the model left (twice) and measures the result. It does not depend on HOW the model designed the scene
(position, typography...): it counts pixels of each color at specific instants. It does NOT measure aesthetics.
(The task prompt and the on-screen text it asks for are in Spanish, so the text check looks for «Lámpara Arco».)

Usage: audio/.venv/bin/python experiment/phase7/evaluate.py <experiment-folder>   ->   writes <folder>/evaluation.json
"""
import json, pathlib, re, shutil, subprocess, sys, time
import numpy as np

D = pathlib.Path(sys.argv[1]).resolve()
BACKGROUND, TEXT, ACCENT = (15, 17, 21), (244, 241, 234), (255, 183, 3)
checks = []
UNREQUESTED_QUALITY = ("standard color format yuv420p", "two renders give the same frames")   # the prompt does not require it: scored separately


def chk(name, ok, detail=""):
    checks.append(dict(name=name, ok=bool(ok), detail=str(detail), category="quality" if name.startswith(UNREQUESTED_QUALITY) else "requirement"))
    print(f"  {'OK   ' if ok else 'FAIL '} {name}" + (f" — {detail}" if detail else ""))


def sh(*a, **kw):
    return subprocess.run([str(x) for x in a], capture_output=True, text=True, **kw)


def count_near(img, color, tol):
    return int(np.sum(np.all(np.abs(img.astype(int) - np.array(color)) <= tol, axis=2)))


def frame(path, t, width=960, height=540):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(path), "-frames:v", "1", "-vf", f"scale={width}:{height}", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], capture_output=True)
    a = np.frombuffer(r.stdout, dtype=np.uint8)
    return a.reshape(height, width, 3) if a.size == width * height * 3 else None


print(f"Evaluating {D.name}")
scene, render = D / "video/scene.html", D / "video/render.mjs"
chk("video/scene.html exists", scene.exists())
chk("video/render.mjs exists", render.exists())
html = scene.read_text(encoding="utf-8", errors="replace") if scene.exists() else ""
js = render.read_text(encoding="utf-8", errors="replace") if render.exists() else ""

chk("defines window.DURATION = 8", re.search(r"window\.DURATION\s*=\s*8\b", html) is not None)
chk("defines window.seek as a function", re.search(r"window\.seek\s*=|function\s+seek|window\[['\"]seek['\"]\]", html) is not None)
chk("contains the text «Lámpara Arco»", "Lámpara Arco" in html)
no_comments = re.sub(r"/\*.*?\*/|<!--.*?-->", "", html, flags=re.S)          # block and HTML comments (they can span several lines)
no_comments = re.sub(r"(?<![:\"'])//[^\n]*", "", no_comments)                 # line comments: WITHOUT re.S, or '//.*' would swallow the whole file
forbidden = re.findall(r"\bDate\b|requestAnimationFrame|setTimeout|setInterval|Math\.random|@keyframes|animation\s*:|transition\s*:", no_comments)
chk("does not use a clock, randomness or CSS animations", not forbidden, "found: " + ", ".join(sorted(set(forbidden))) if forbidden else "")

# ---- run the render twice
times, render_ok = [], []
for i in (1, 2):
    (D / "out").mkdir(exist_ok=True)
    target = D / "out/titulo.mp4"          # the prompt asks for exactly this output name
    if target.exists(): target.unlink()
    t0 = time.time()
    try:
        r = sh("node", "video/render.mjs", cwd=D, timeout=240)
        ok = r.returncode == 0 and target.exists() and target.stat().st_size > 5000
        detail = "" if ok else (r.stderr or r.stdout)[-300:]
    except subprocess.TimeoutExpired:
        ok, detail = False, "timed out (240 s)"
    times.append(time.time() - t0); render_ok.append(ok)
    if ok: shutil.copy(target, D / f"out/render_{i}.mp4")
    if i == 1: chk("`node video/render.mjs` finishes fine and creates out/titulo.mp4", ok, f"{times[0]:.1f} s" if ok else detail)
if not render_ok[0]:
    result = dict(folder=D.name, passed=sum(c["ok"] for c in checks), total=len(checks) + 9, checks=checks, render_seconds=None, note="the render does not work: the other measurements are skipped")
    (D / "evaluation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRESULT: {result['passed']}/{result['total']} (the render does not work)"); sys.exit(1)

v1 = D / "out/render_1.mp4"
info = json.loads(sh("ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_read_frames,pix_fmt,duration", "-of", "json", v1).stdout)["streams"][0]
chk("H.264 video, 1920x1080, 30 fps", info["codec_name"] == "h264" and (info["width"], info["height"]) == (1920, 1080) and info["r_frame_rate"] == "30/1",
    f'{info["codec_name"]} {info["width"]}x{info["height"]} {info["r_frame_rate"]}')
chk("240 frames (8 s)", int(info.get("nb_read_frames", 0)) == 240, f'{info.get("nb_read_frames")} frames, {float(info.get("duration", 0)):.2f} s')
chk("standard color format yuv420p (not yuvj420p)", info["pix_fmt"] == "yuv420p", info["pix_fmt"])

# ---- content: count pixels of each color at specific instants (layout-agnostic)
F = {t: frame(v1, t) for t in (0.0, 0.4, 1.0, 1.8, 2.4, 3.2, 4.0, 7.9)}
frames_ok = all(f is not None for f in F.values())
chk("all sample frames can be extracted", frames_ok)
if frames_ok:
    total = 960 * 540
    bg0 = count_near(F[0.0], BACKGROUND, 12) / total
    chk("t = 0 s: only the #0f1115 background (≥ 99 % of the pixels)", bg0 >= 0.99, f"{100 * bg0:.2f} % background")
    txt = {t: count_near(F[t], TEXT, 40) for t in F}
    chk("the text fades in (nothing at 0.4 s; partial at 1.0 s; complete at 2.4 s)", txt[0.4] < 200 and txt[1.0] < txt[2.4] * 0.85 and txt[2.4] > 3000,
        f"text-colored pixels: 0.4 s→{txt[0.4]} · 1.0 s→{txt[1.0]} · 2.4 s→{txt[2.4]}")
    line = {t: count_near(F[t], ACCENT, 45) for t in F}
    chk("the accent line grows from 1 s to 3 s (nothing at 1.0 s and more and more afterwards)", line[1.0] < 40 and line[1.0] < line[1.8] < line[2.4] < line[3.2] * 0.97 and line[3.2] >= 100,
        f"accent pixels: 1.0 s→{line[1.0]} · 1.8→{line[1.8]} · 2.4→{line[2.4]} · 3.2→{line[3.2]} · 4.0→{line[4.0]}")
    chk("the line ends complete and the scene stays stable (t = 4 s ≈ t = 7.9 s)", float(np.mean(np.abs(F[4.0].astype(int) - F[7.9].astype(int)))) < 2.0 and abs(line[4.0] - line[3.2]) <= 0.03 * max(1, line[4.0]),
        f"mean difference 4 s vs 7.9 s: {float(np.mean(np.abs(F[4.0].astype(int) - F[7.9].astype(int)))):.2f}")
else:
    for n in ("t = 0 s: only background", "text fades in", "line grows", "scene stable"): chk(n, False, "no frames")

# ---- determinism: two renders -> same frames
def fingerprint(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v", "-f", "framemd5", "-"], capture_output=True, text=True)
    return [l.split(",")[-1] for l in r.stdout.splitlines() if l and not l.startswith("#")]
if render_ok[1]:
    h1, h2 = fingerprint(D / "out/render_1.mp4"), fingerprint(D / "out/render_2.mp4")
    same = sum(a == b for a, b in zip(h1, h2))
    chk("two renders give the same frames (deterministic)", h1 == h2 and len(h1) == 240, f"{same}/{len(h1)} identical frames")
else:
    chk("two renders give the same frames (deterministic)", False, "the second render failed")

req = [c for c in checks if c["category"] == "requirement"]; qual = [c for c in checks if c["category"] == "quality"]
passed = sum(c["ok"] for c in checks)
result = dict(folder=D.name, passed=passed, total=len(checks), requirements_ok=sum(c["ok"] for c in req), requirements_total=len(req),
              quality_ok=sum(c["ok"] for c in qual), quality_total=len(qual), checks=checks, render_seconds=round(sum(times) / len(times), 1))
(D / "evaluation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nRESULT: prompt requirements {result['requirements_ok']}/{result['requirements_total']} · unrequested quality {result['quality_ok']}/{result['quality_total']} · render {result['render_seconds']} s")
sys.exit(0 if passed == len(checks) else 1)
