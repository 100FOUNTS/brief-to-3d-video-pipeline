#!/usr/bin/env python3
"""Checks that the voice is intelligible: transcribes it with Whisper (local, mlx-audio) and computes the WER against docs/script.json.
WER = (substitutions + deletions + insertions) / words in the script. 0 % = identical. It measures intelligibility,
NOT naturalness: whether the voice sounds pleasant can only be judged by listening to it.
The narration is in Spanish, so the transcription runs with --language es.
Usage: audio/.venv/bin/python audio/verify_voice.py out/audio/voice_ef_dora.wav [...]"""
import json, os, re, sys, subprocess, pathlib, unicodedata
ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL = os.environ.get("WHISPER_MODEL", "mlx-community/whisper-large-v3-asr-fp16")   # the full large model (3 GB); change it with WHISPER_MODEL

def normalize(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")          # no accents: the recognizer places them its own way
    return re.findall(r"[a-zñ0-9]+", t)

def distances(ref, hyp):
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
    return d

def wer(ref, hyp):
    """Full WER: also counts anything extra the recognizer invents."""
    return distances(ref, hyp)[len(hyp)] / max(1, len(ref))

def wer_without_tail(ref, hyp):
    """WER without penalizing text invented AFTER the script ends (Whisper hallucinates in trailing silences)."""
    return min(distances(ref, hyp)) / max(1, len(ref))

script = " ".join(s["text"] for s in json.loads((ROOT / "docs/script.json").read_text(encoding="utf-8"))["segments"])
ref = normalize(script)
for path in sys.argv[1:]:
    p = pathlib.Path(path)
    base = ROOT / "out/audio/transcript" / p.stem
    base.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, "-m", "mlx_audio.stt.generate", "--model", MODEL, "--audio", str(p), "--output-path", str(base), "--format", "txt", "--language", "es"],
                   capture_output=True, text=True)
    if not list(base.parent.glob(p.stem + '*')):
        sys.exit('The recognizer failed:\n' + (r.stderr or '')[-800:])
    cand = sorted(base.parent.glob(p.stem + "*.txt")) or sorted(base.parent.glob("*.txt"))
    text = cand[-1].read_text(encoding="utf-8").strip() if cand else ""
    hyp = normalize(text)
    print(f"\n{p.name}\n  script    : {script}\n  heard     : {text}\n  full WER       : {100 * wer(ref, hyp):.1f} %\n  WER without the invented tail: {100 * wer_without_tail(ref, hyp):.1f} %   ({len(ref)} script words)")
