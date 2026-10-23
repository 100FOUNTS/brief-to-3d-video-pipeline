#!/usr/bin/env python3
"""Automatic checks of the output of `make studio` (Phase 6). Exits with 1 if any of them fails.

Covers what each piece on its own cannot see: that the FINAL video has picture and audio, that it is as long as it should be,
that the loudness is the agreed one, that the video background color is the brief's, that there is voice in every window and that the .glb has all 7 parts.
It does NOT measure whether the voice sounds natural or whether the design is pretty: that is judged by looking and listening.

Usage: audio/.venv/bin/python scripts/verify_output.py [--brief brief.json]
"""
import argparse, json, pathlib, re, struct, subprocess, sys, wave
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
PARTS = ["base", "lower-arm", "lower-joint", "upper-arm", "upper-joint", "shade", "bulb"]
results = []


def chk(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  {'OK   ' if ok else 'FAIL '} {name}" + (f" — {detail}" if detail else ""))


def sh(*args):
    return subprocess.run([str(a) for a in args], capture_output=True, text=True)


def frame(path, t, width, height, pix_fmt):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(path), "-frames:v", "1", "-vf", f"scale={width}:{height}", "-pix_fmt", pix_fmt, "-f", "rawvideo", "-"], capture_output=True)
    return np.frombuffer(r.stdout, dtype=np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", default="brief.json")
    a = ap.parse_args()
    brief = json.loads((ROOT / a.brief).read_text(encoding="utf-8"))
    voice = brief["voice"]
    label = voice["name"] if voice["engine"] == "kokoro" else f'{voice["engine"]}-{voice["name"]}'
    final = ROOT / "out/promo-final.mp4"
    print(f"Verifying the output of '{brief['product']['name']}' ({a.brief})")

    print("\nFiles")
    for rel, minimum in [("out/promo-final.mp4", 100_000), ("out/lamp.glb", 10_000), ("viewer/dist/index.html", 200), (f"out/audio/mix_{label}.wav", 100_000), ("out/promo-hyperframes.mp4", 100_000)]:
        p = ROOT / rel
        chk(rel, p.exists() and p.stat().st_size >= minimum, f"{p.stat().st_size / 1e6:.2f} MB" if p.exists() else "does not exist")
    if not final.exists():
        sys.exit(1)

    print("\nFinal video")
    info = json.loads(sh("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", final).stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), {})
    chk("H.264 video, 1920x1080, 30 fps", v.get("codec_name") == "h264" and (v.get("width"), v.get("height")) == (1920, 1080) and v.get("r_frame_rate") == "30/1",
        f'{v.get("codec_name")} {v.get("width")}x{v.get("height")} {v.get("r_frame_rate")}')
    dur_v = float(v.get("duration", 0)); dur_a = float(au.get("duration", 0))
    chk("duration 20.0 s (±0.1)", abs(dur_v - brief["video"]["duration"]) <= 0.1, f"{dur_v:.2f} s")
    chk("has an AAC audio track at 48 kHz", au.get("codec_name") == "aac" and au.get("sample_rate") == "48000", f'{au.get("codec_name")} {au.get("sample_rate")} Hz')
    chk("audio and video last the same (±0.15 s)", abs(dur_v - dur_a) <= 0.15, f"video {dur_v:.2f} s · audio {dur_a:.2f} s")

    print("\nAudio")
    r = sh("ffmpeg", "-hide_banner", "-nostats", "-i", final, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-")
    integrated = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr); peak = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    li, lp = (float(integrated[-1]) if integrated else None), (float(peak[-1]) if peak else None)
    chk("integrated loudness -16 LUFS (±1)", li is not None and abs(li + 16) <= 1, f"{li} LUFS")
    chk("true peak <= -1.0 dBFS (no clipping)", lp is not None and lp <= -1.0, f"{lp} dBFS")
    # voice present in every script window
    script = json.loads((ROOT / "docs/script.json").read_text(encoding="utf-8"))["segments"]
    with wave.open(str(ROOT / f"out/audio/voice_{label}.wav")) as w:
        sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
    report = json.loads((ROOT / f"out/audio/voice_{label}.json").read_text(encoding="utf-8"))
    for s, inf in zip(script, report):
        chunk = x[int(s["start"] * sr): int((s["start"] + inf["duration"]) * sr)]
        rms = float(np.sqrt(np.mean(chunk ** 2))) if chunk.size else 0
        chk(f"voice present in '{s['id']}' ({s['start']:.1f}–{inf['end']:.1f} s) and fits its window", rms > 0.02 and inf["fits"], f"RMS {rms:.3f}, {inf['duration']:.2f}/{inf['window']:.1f} s")

    print("\nPicture")
    times = [1, 3.5, 6, 10, 14, 18.5]
    gray = [frame(final, t, 32, 18, "gray").astype(np.float32) for t in times]
    chk("no sample frame is empty", all(g.size == 32 * 18 for g in gray), "ffmpeg returned a picture for all 6 samples")
    changes = [float(np.mean(np.abs(gray[i] - gray[i + 1]))) for i in range(len(gray) - 1)]
    chk("the video changes over time (it is not frozen)", sum(c > 2 for c in changes) >= 4, "difference between samples: " + ", ".join(f"{c:.1f}" for c in changes))
    rgb = frame(final, 10, 64, 36, "rgb24").reshape(36, 64, 3).astype(int)
    corner = rgb[1, 1]
    target = np.array([int(brief["palette"]["background"][i:i + 2], 16) for i in (1, 3, 5)])
    chk("the video background color is the brief's (±14 per channel)", np.all(np.abs(corner - target) <= 14), f"video {tuple(int(c) for c in corner)} · brief {tuple(int(c) for c in target)} ({brief['palette']['background']})")

    print("\nViewer")
    viewer_glb = ROOT / "viewer/dist/lamp.glb"
    same = viewer_glb.exists() and viewer_glb.read_bytes() == (ROOT / "out/lamp.glb").read_bytes()
    chk("the viewer carries the Blender .glb (the same file as out/lamp.glb)", same,
        "identical" if same else "does not exist or differs: was the viewer built after Blender?")

    print("\n3D model (.glb)")
    d = (ROOT / "out/lamp.glb").read_bytes()
    n = struct.unpack("<I", d[12:16])[0]
    nodes = [x["name"] for x in json.loads(d[20:20 + n])["nodes"]]
    missing = [p for p in PARTS if p not in nodes]
    chk("contains the 7 parts by name", not missing, "missing: " + ", ".join(missing) if missing else f"{len(nodes)} nodes")

    ok = all(results)
    print(f"\n{'ALL CORRECT' if ok else 'THERE ARE FAILURES'}: {sum(results)}/{len(results)} checks")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
