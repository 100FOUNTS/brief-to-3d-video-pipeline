#!/usr/bin/env python3
"""Ambient music synthesized with numpy (no samples or third-party files). Phase 5.

70 bpm, C major. Progression Cmaj7 | Am7 | Fmaj7 | G6sus | Cmaj7 | Fmaj7. Layers: soft pad, arpeggio, a discreet kick
at the start of each bar and reverb by convolution with a synthetic impulse response.
The music accompanies the video scenes: the arpeggio enters with the light (2.3 s) and the brightness rises when the light turns golden (13 s).

Usage:  audio/.venv/bin/python audio/music.py [--duration 20] [--out out/audio/music.wav] [--seed 7]
Output: stereo WAV, 48 kHz, 16-bit. Deterministic: the only randomness (reverb noise) uses a fixed seed.
"""
import argparse, wave, pathlib
import numpy as np

SR = 48000
BPM = 70.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
ROOT = pathlib.Path(__file__).resolve().parent.parent


def note(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


# Chords as MIDI notes (middle C = 60)
CHORDS = [
    [48, 55, 59, 64, 67],   # Cmaj7  : C3 G3 B3 E4 G4
    [45, 55, 60, 64, 67],   # Am7    : A2 G3 C4 E4 G4
    [41, 52, 57, 60, 64],   # Fmaj7  : F2 E3 A3 C4 E4
    [43, 53, 57, 60, 62],   # G6sus  : G2 F3 A3 C4 D4  (suspended: soft tension)
    [48, 55, 59, 64, 67],   # Cmaj7
    [41, 52, 57, 60, 64],   # Fmaj7
]


def envelope(n, attack, release, sr=SR):
    e = np.ones(n)
    a, r = int(attack * sr), int(release * sr)
    if a: e[:a] = np.linspace(0, 1, a) ** 2
    if r: e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def pad(freq, dur, phase=0.0):
    t = np.arange(int(dur * SR)) / SR
    # three slightly detuned oscillators ("chorus" effect) with sine + a little third harmonic
    x = np.zeros_like(t)
    for cents in (-6, 0, 6):
        f = freq * 2 ** (cents / 1200)
        x += np.sin(2 * np.pi * f * t + phase) + 0.18 * np.sin(2 * np.pi * 3 * f * t + phase)
    return x / 3.0 * envelope(t.size, 1.4, 1.6)


def pluck(freq, dur=1.6):
    t = np.arange(int(dur * SR)) / SR
    x = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t) + 0.12 * np.sin(2 * np.pi * 3 * freq * t)
    return x * np.exp(-t * 3.2) * envelope(t.size, 0.004, 0.05)


def kick(dur=0.5):
    t = np.arange(int(dur * SR)) / SR
    f = 42 + 60 * np.exp(-t * 28)                       # the pitch drops from ~100 Hz to 42 Hz
    phase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(phase) * np.exp(-t * 9) * envelope(t.size, 0.002, 0.02)


def add(dest, chunk, start, gain, pan):
    """Adds a mono chunk into a stereo buffer with panning pan in [-1, 1]."""
    i0 = int(start * SR)
    if i0 >= dest.shape[0]:
        return
    n = min(chunk.size, dest.shape[0] - i0)
    left, right = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    dest[i0:i0 + n, 0] += chunk[:n] * gain * left
    dest[i0:i0 + n, 1] += chunk[:n] * gain * right


def reverb(x, rng, seconds=1.8, mix=0.28):
    """Reverb by convolution with a synthetic impulse response (noise with exponential decay, darkened)."""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-t * 3.4)[:, None]
    for k in range(1, ir.shape[0]):                      # very simple low-pass filter: dampens the highs of the tail
        ir[k] = 0.35 * ir[k] + 0.65 * ir[k - 1]
    ir /= np.sqrt(np.sum(ir ** 2, axis=0, keepdims=True))
    total = x.shape[0] + n
    nfft = 1 << (total - 1).bit_length()
    out = np.empty((x.shape[0], 2))
    for c in range(2):
        y = np.fft.irfft(np.fft.rfft(x[:, c], nfft) * np.fft.rfft(ir[:, c], nfft), nfft)[: x.shape[0]]
        out[:, c] = (1 - mix) * x[:, c] + mix * y
    return out


def compose(duration, seed):
    rng = np.random.default_rng(seed)
    n = int(duration * SR)
    dry = np.zeros((n, 2))
    n_bars = int(np.ceil(duration / BAR)) + 1

    for c in range(n_bars):
        t0 = c * BAR
        chord = CHORDS[c % len(CHORDS)]
        # pad: each note lasts a little longer than the bar so chords overlap
        for k, m in enumerate(chord):
            add(dry, pad(note(m), BAR + 1.2, phase=k), t0, 0.075 if m < 50 else 0.05, pan=(-0.5 + 0.25 * k))
        # discreet kick at the start of each bar (and a softer hit on beat three)
        add(dry, kick(), t0, 0.30, 0.0)
        add(dry, kick(), t0 + 2 * BEAT, 0.13, 0.0)
        # eighth-note arpeggio with the chord's high notes; enters at 2.3 s with the light
        if t0 + BAR > 2.3:
            highs = [m + 12 for m in chord[2:]] + [chord[1] + 12]
            pattern = [0, 1, 2, 3, 2, 1, 3, 2]
            for j, idx in enumerate(pattern):
                ti = t0 + j * BEAT / 2
                if ti < 2.3:
                    continue
                brightness = 1.0 + 0.55 * (ti >= 13.0)    # when the light turns golden, the arpeggio gets brighter
                add(dry, pluck(note(highs[idx % len(highs)])), ti, 0.055 * brightness, pan=(-0.6 if j % 2 == 0 else 0.6))

    dry = dry[:n]
    x = reverb(dry, rng)
    # soft fade in and out (the video fades in from and out to black)
    fade_in = np.minimum(1, np.arange(n) / (SR * 1.0)) ** 2
    fade_out = np.minimum(1, (n - np.arange(n)) / (SR * 0.9)) ** 2
    x *= (fade_in * fade_out)[:, None]
    peak = np.max(np.abs(x))
    return x / peak * 0.708                               # peak at -3 dBFS


def save(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=float, default=20.0)
    ap.add_argument("--out", default="out/audio/music.wav")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--brief", default="", help="brief.json: music.bpm and music.seed")
    a = ap.parse_args()
    global BPM, BEAT, BAR
    if a.brief:
        import json
        m = json.load(open(ROOT / a.brief if not pathlib.Path(a.brief).is_absolute() else a.brief, encoding="utf-8"))["music"]
        BPM, a.seed = float(m["bpm"]), int(m["seed"])
        BEAT, BAR = 60.0 / BPM, 4 * (60.0 / BPM)
    dest = ROOT / a.out
    dest.parent.mkdir(parents=True, exist_ok=True)
    x = compose(a.duration, a.seed)
    save(dest, x)
    print(f"OK {a.out}: {x.shape[0] / SR:.2f} s, {SR} Hz, stereo, peak {20 * np.log10(np.max(np.abs(x))):.1f} dBFS")


if __name__ == "__main__":
    main()
