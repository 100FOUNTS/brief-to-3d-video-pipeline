#!/usr/bin/env python3
"""Promo voice-over with Kokoro-82M (mlx-audio, Apple Silicon). Phase 5.

Reads docs/script.json (one sentence per scene, with its start second and its window), generates each sentence,
checks that it fits in its window (if not, speeds it up just enough) and places them on a 20 s track.

Usage:  audio/.venv/bin/python audio/narration.py [--engine kokoro|qwen3] [--voices ef_dora,em_alex] [--instruct "..."] [--duration 20] [--out out/audio]
Engines: kokoro (Kokoro-82M, 0.39 GB) · qwen3 (Qwen3-TTS 1.7B CustomVoice 8-bit, 3.08 GB; preset speakers with Spanish forced)
Output: out/audio/voice_<label>.wav (mono, 20 s) · out/audio/<label>/<id>.wav · out/audio/voice_<label>.json (report)
  label = the voice (kokoro) or "<engine>-<voice>" (other engines), so Kokoro's files are not overwritten.

The narration language is Spanish (the product content), so the text normalizer and the Whisper check below are Spanish-specific.
"""
import argparse, json, wave, pathlib, logging, re, subprocess, tempfile, unicodedata
import numpy as np

logging.getLogger().setLevel(logging.ERROR)
ROOT = pathlib.Path(__file__).resolve().parent.parent
ENGINES = {
    "kokoro": dict(model="mlx-community/Kokoro-82M-bf16", lang="e", voices="ef_dora,em_alex"),
    # qwen3 ignores 'speed' and its pace varies a lot between seeds (the same sentence: 5 to 9.6 s): several candidates are generated,
    # the shortest one that Whisper confirms as correct is chosen, and only then is it sped up with ffmpeg.
    "qwen3": dict(model="mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit", lang="spanish", voices="ryan,aiden",
                  no_speed=True, candidates=5,
                  instruct="Speak at a brisk, natural narration pace. Do not drag words or pause for long."),
}
STT_MODEL = "mlx-community/whisper-large-v3-asr-fp16"
ATEMPO_MAX = 1.25      # maximum later speed-up with ffmpeg (pitch unchanged)
SR = 24000             # overwritten with the model's real sample rate
SEED = 0               # fixed seed: the voice is regenerated identically (qwen3 uses its own seeds per candidate)
MARGIN = 0.15          # seconds left free at the end of each window
SPEED_MAX = 1.30       # not sped up beyond this: the voice becomes unnatural


def save_wav(path, audio, sr):
    pcm = np.clip(audio, -1.0, 1.0)
    pcm = (pcm * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


def trim_silence(a, threshold=0.004, tail=0.05):
    """Removes the leading and trailing silence of a sentence (keeps `tail` s) so that 'start' means 'starts speaking'."""
    idx = np.where(np.abs(a) > threshold)[0]
    if idx.size == 0:
        return a
    i0 = max(0, idx[0] - int(0.02 * SR)); i1 = min(a.size, idx[-1] + int(tail * SR))
    return a[i0:i1]


def generate(model, text, voice, speed, lang, instruct=None, no_speed=False):
    import mlx.core as mx
    if not no_speed:
        mx.random.seed(SEED)                          # Kokoro uses internal random noise: without a fixed seed every run gives a different waveform
    kw = dict(text=text, voice=voice, lang_code=lang)
    if not no_speed:
        kw["speed"] = speed
    if instruct:
        kw["instruct"] = instruct
    chunks = [np.array(r.audio, dtype=np.float32) for r in model.generate(**kw)]
    return trim_silence(np.concatenate(chunks))


def normalize(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-zñ0-9]+", t)


def word_errors(ref, hyp):
    """Edit distance between word lists (substitutions + deletions + insertions)."""
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
    return d[len(hyp)]


def transcribe(stt, audio):
    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / "c.wav"
        save_wav(path, audio, SR)
        r = stt.generate(str(path), language="es")
        return getattr(r, "text", str(r)).strip()


def speed_up(audio, factor):
    """Speeds up without changing the pitch, using ffmpeg's atempo filter."""
    with tempfile.TemporaryDirectory() as td:
        a, b = pathlib.Path(td) / "a.wav", pathlib.Path(td) / "b.wav"
        save_wav(a, audio, SR)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(a), "-filter:a", f"atempo={factor}", str(b)], check=True)
        with wave.open(str(b)) as w:
            return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768


def best_candidate(model, stt, text, voice, cfg, instruct):
    """Generates N candidates with fixed seeds and returns the shortest one whose text Whisper confirms (or the one with fewest errors)."""
    import mlx.core as mx
    ref = normalize(text)
    cands = []
    for k in range(cfg["candidates"]):
        mx.random.seed(k)
        a = generate(model, text, voice, 1.0, cfg["lang"], instruct, no_speed=True)
        cands.append(dict(seed=k, audio=a, dur=a.size / SR))
    for c in sorted(cands, key=lambda c: c["dur"]):
        c["heard"] = transcribe(stt, c["audio"])
        c["err"] = word_errors(ref, normalize(c["heard"]))
        if c["err"] == 0:
            return c, cands
    return min(cands, key=lambda c: (c.get("err", 99), c["dur"])), cands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=None, choices=list(ENGINES))
    ap.add_argument("--brief", default="", help="brief.json: voice.engine and voice.name (if --engine/--voices are not given)")
    ap.add_argument("--voices", default=None)
    ap.add_argument("--instruct", default=None, help="style instruction (only for engines that support it, e.g. qwen3)")
    ap.add_argument("--extra-window", type=float, default=0.0, help="seconds added to every window (for voices slower than the script)")
    ap.add_argument("--duration", type=float, default=20.0)
    ap.add_argument("--out", default="out/audio")
    a = ap.parse_args()
    from mlx_audio.tts.utils import load_model
    global SR
    if a.brief:
        bv = json.loads((ROOT / a.brief if not pathlib.Path(a.brief).is_absolute() else pathlib.Path(a.brief)).read_text(encoding="utf-8"))["voice"]
        a.engine = a.engine or bv["engine"]
        a.voices = a.voices or bv["name"]
    a.engine = a.engine or "kokoro"
    cfg = ENGINES[a.engine]
    model = load_model(cfg["model"])
    SR = int(getattr(model, "sample_rate", SR))
    voices = (a.voices or cfg["voices"]).split(",")
    instruct = a.instruct if a.instruct is not None else cfg.get("instruct")
    stt = None
    if cfg.get("no_speed"):
        from mlx_audio.stt.utils import load_model as load_stt
        stt = load_stt(STT_MODEL)
    script = json.loads((ROOT / "docs/script.json").read_text(encoding="utf-8"))["segments"]
    out_dir = ROOT / a.out
    out_dir.mkdir(parents=True, exist_ok=True)
    exit_code = 0

    for voice in voices:
        label = voice if a.engine == "kokoro" else f"{a.engine}-{voice}"
        (out_dir / label).mkdir(exist_ok=True)
        track = np.zeros(int(a.duration * SR), dtype=np.float32)
        report = []
        for s in script:
            speed = 1.0
            window = s["window"] + a.extra_window
            extra = {}
            if cfg.get("no_speed"):
                c, all_cands = best_candidate(model, stt, s["text"], voice, cfg, instruct)
                audio, dur = c["audio"], c["dur"]
                extra = dict(seed=c["seed"], heard=c["heard"], word_errors=c["err"], candidates=[round(x["dur"], 2) for x in all_cands])
                if dur > window - MARGIN:                                # does not fit: sped up with ffmpeg just enough
                    speed = min(ATEMPO_MAX, round(dur / (window - MARGIN) + 0.02, 2))
                    audio = speed_up(audio, speed)
                    dur = audio.size / SR
            else:
                audio = generate(model, s["text"], voice, speed, cfg["lang"], instruct)
                dur = audio.size / SR
                while dur > window - MARGIN and speed < SPEED_MAX:        # does not fit: sped up in 5 % steps
                    speed = round(speed + 0.05, 2)
                    audio = generate(model, s["text"], voice, speed, cfg["lang"], instruct)
                    dur = audio.size / SR
            fits = dur <= window - MARGIN + 1e-9
            end = s["start"] + dur
            if not fits or end > a.duration:
                exit_code = 1
            i0 = int(s["start"] * SR)
            track[i0:i0 + audio.size] += audio[: max(0, track.size - i0)]
            save_wav(out_dir / label / f"{s['id']}.wav", audio, SR)
            report.append(dict(id=s["id"], start=s["start"], end=round(end, 2), duration=round(dur, 2), window=window,
                               speed=speed, fits=fits, peak=round(float(np.max(np.abs(audio))), 3), **extra))
        peak = float(np.max(np.abs(track)))
        if peak > 0.98:
            track *= 0.98 / peak                                          # avoids clipping when summing
        save_wav(out_dir / f"voice_{label}.wav", track, SR)
        (out_dir / f"voice_{label}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n== {a.engine} · {voice} ==")
        for r in report:
            print(f"  {r['id']:<14} {r['start']:>5.1f}→{r['end']:>5.2f} s  dur {r['duration']:.2f} / window {r['window']:.1f}  speed {r['speed']:.2f}  {'OK' if r['fits'] else 'DOES NOT FIT'}"
                  + (f"  [candidates {r['candidates']} → seed {r['seed']}, errors {r['word_errors']}]" if 'seed' in r else ""))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
