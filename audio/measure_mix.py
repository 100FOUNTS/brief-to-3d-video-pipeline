#!/usr/bin/env python3
"""Measures, in each speech window, how much louder the voice is than the already-ducked music (LU). Uses the same filters as mix.sh.
Rule of thumb for narration over music: voice >= ~10 LU above the music. Usage: audio/.venv/bin/python audio/measure_mix.py [voice]"""
import json, math, re, subprocess, sys, pathlib
VOICE_WEIGHT = 1.7      # the same weight audio/mix.sh uses in amix (the voice enters 1.7 times louder than the music)
VOICE_GAIN_DB = 20 * math.log10(VOICE_WEIGHT)
ROOT = pathlib.Path(__file__).resolve().parent.parent
voice = sys.argv[1] if len(sys.argv) > 1 else "ef_dora"
tmp = ROOT / "out/audio/tmp"; tmp.mkdir(parents=True, exist_ok=True)
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", ROOT / "out/audio/music.wav", "-i", ROOT / f"out/audio/voice_{voice}.wav", "-filter_complex",
    "[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,asplit=2[vsc][v2];[0:a]volume=-2dB[m];[m][vsc]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=450:makeup=1[mduck]",
    "-map", "[mduck]", tmp / "music_duck.wav", "-map", "[v2]", tmp / "voice.wav"], check=True)
def lufs(file, a, b):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", str(a), "-t", str(b - a), "-i", file, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return float(m[-1]) if m else float("-inf")
seg = json.loads((ROOT / f"out/audio/voice_{voice}.json").read_text())
print(f"Voice {voice}: voice and music level inside each speech window")
worst = 99
for s in seg:
    a, b = s["start"] + 0.1, s["end"] - 0.05
    if b - a < 0.4:                                       # ebur128 needs >= 0.4 s: with less it returns -65 LUFS (garbage)
        print(f"  {s['id']:<14} window of {b - a:.2f} s: too short to measure loudness (skipped)")
        continue
    v, m = lufs(tmp / "voice.wav", a, b), lufs(tmp / "music_duck.wav", a, b)
    diff = v + VOICE_GAIN_DB - m                        # real difference in the mix, with the voice weight
    worst = min(worst, diff)
    print(f"  {s['id']:<14} voice {v + VOICE_GAIN_DB:6.1f}  music {m:6.1f}   difference {diff:+5.1f} LU")
no_duck = lufs(ROOT / "out/audio/music.wav", 5.6, 7.7)
duck = lufs(tmp / "music_duck.wav", 5.6, 7.7)
print(f"Ducking effect at 5.6–7.7 s: music {no_duck:.1f} → {duck:.1f} LUFS ({duck - no_duck:+.1f} LU)")
print(f"WORST voice–music difference: {worst:+.1f} LU")
