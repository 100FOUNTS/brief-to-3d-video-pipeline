#!/usr/bin/env python3
"""Música ambiental sintetizada con numpy (sin samples ni archivos de terceros). Fase 5.

70 bpm, Do mayor. Progresión Cmaj7 | Am7 | Fmaj7 | G6sus | Cmaj7 | Fmaj7. Capas: pad suave, arpegio, un bombo discreto
al inicio de cada compás y reverberación por convolución con una respuesta sintética.
La música acompaña a las escenas del vídeo: el arpegio entra con la luz (2,3 s) y el brillo sube cuando la luz vira al dorado (13 s).

Uso:  audio/.venv/bin/python audio/music.py [--duracion 20] [--out out/audio/musica.wav] [--semilla 7]
Salida: WAV estéreo 48 kHz, 16 bits. Determinista: la única aleatoriedad (ruido de la reverberación) usa una semilla fija.
"""
import argparse, wave, pathlib
import numpy as np

SR = 48000
BPM = 70.0
BEAT = 60.0 / BPM
COMPAS = 4 * BEAT
RAIZ = pathlib.Path(__file__).resolve().parent.parent


def nota(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


# Acordes como notas MIDI (Do central = 60)
ACORDES = [
    [48, 55, 59, 64, 67],   # Cmaj7  : C3 G3 B3 E4 G4
    [45, 55, 60, 64, 67],   # Am7    : A2 G3 C4 E4 G4
    [41, 52, 57, 60, 64],   # Fmaj7  : F2 E3 A3 C4 E4
    [43, 53, 57, 60, 62],   # G6sus  : G2 F3 A3 C4 D4  (suspendido: tensión suave)
    [48, 55, 59, 64, 67],   # Cmaj7
    [41, 52, 57, 60, 64],   # Fmaj7
]


def envolvente(n, ataque, liberacion, sr=SR):
    e = np.ones(n)
    a, r = int(ataque * sr), int(liberacion * sr)
    if a: e[:a] = np.linspace(0, 1, a) ** 2
    if r: e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def pad(freq, dur, fase=0.0):
    t = np.arange(int(dur * SR)) / SR
    # tres osciladores ligeramente desafinados (efecto "coro") con seno + un poco de tercer armónico
    x = np.zeros_like(t)
    for cents in (-6, 0, 6):
        f = freq * 2 ** (cents / 1200)
        x += np.sin(2 * np.pi * f * t + fase) + 0.18 * np.sin(2 * np.pi * 3 * f * t + fase)
    return x / 3.0 * envolvente(t.size, 1.4, 1.6)


def pluck(freq, dur=1.6):
    t = np.arange(int(dur * SR)) / SR
    x = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t) + 0.12 * np.sin(2 * np.pi * 3 * freq * t)
    return x * np.exp(-t * 3.2) * envolvente(t.size, 0.004, 0.05)


def bombo(dur=0.5):
    t = np.arange(int(dur * SR)) / SR
    f = 42 + 60 * np.exp(-t * 28)                       # el tono baja de ~100 Hz a 42 Hz
    fase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(fase) * np.exp(-t * 9) * envolvente(t.size, 0.002, 0.02)


def sumar(destino, trozo, inicio, ganancia, pan):
    """Suma un trozo mono en un buffer estéreo con panorámica pan en [-1, 1]."""
    i0 = int(inicio * SR)
    if i0 >= destino.shape[0]:
        return
    n = min(trozo.size, destino.shape[0] - i0)
    izq, der = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    destino[i0:i0 + n, 0] += trozo[:n] * ganancia * izq
    destino[i0:i0 + n, 1] += trozo[:n] * ganancia * der


def reverb(x, rng, segundos=1.8, mezcla=0.28):
    """Reverberación por convolución con una respuesta sintética (ruido con decaimiento exponencial, oscurecida)."""
    n = int(segundos * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-t * 3.4)[:, None]
    for k in range(1, ir.shape[0]):                      # filtro paso bajo muy simple: apaga los agudos de la cola
        ir[k] = 0.35 * ir[k] + 0.65 * ir[k - 1]
    ir /= np.sqrt(np.sum(ir ** 2, axis=0, keepdims=True))
    largo = x.shape[0] + n
    nfft = 1 << (largo - 1).bit_length()
    salida = np.empty((x.shape[0], 2))
    for c in range(2):
        y = np.fft.irfft(np.fft.rfft(x[:, c], nfft) * np.fft.rfft(ir[:, c], nfft), nfft)[: x.shape[0]]
        salida[:, c] = (1 - mezcla) * x[:, c] + mezcla * y
    return salida


def componer(duracion, semilla):
    rng = np.random.default_rng(semilla)
    n = int(duracion * SR)
    capas_seco = np.zeros((n, 2))
    n_compases = int(np.ceil(duracion / COMPAS)) + 1

    for c in range(n_compases):
        t0 = c * COMPAS
        acorde = ACORDES[c % len(ACORDES)]
        # pad: cada nota dura un poco más que el compás para que los acordes se solapen
        for k, m in enumerate(acorde):
            sumar(capas_seco, pad(nota(m), COMPAS + 1.2, fase=k), t0, 0.075 if m < 50 else 0.05, pan=(-0.5 + 0.25 * k))
        # bombo discreto al inicio de cada compás (y un golpe más suave en el tercer tiempo)
        sumar(capas_seco, bombo(), t0, 0.30, 0.0)
        sumar(capas_seco, bombo(), t0 + 2 * BEAT, 0.13, 0.0)
        # arpegio de corcheas con las notas agudas del acorde; entra a los 2,3 s con la luz
        if t0 + COMPAS > 2.3:
            agudos = [m + 12 for m in acorde[2:]] + [acorde[1] + 12]
            patron = [0, 1, 2, 3, 2, 1, 3, 2]
            for j, idx in enumerate(patron):
                ti = t0 + j * BEAT / 2
                if ti < 2.3:
                    continue
                brillo = 1.0 + 0.55 * (ti >= 13.0)       # cuando la luz vira al dorado, el arpegio brilla más
                sumar(capas_seco, pluck(nota(agudos[idx % len(agudos)])), ti, 0.055 * brillo, pan=(-0.6 if j % 2 == 0 else 0.6))

    capas_seco = capas_seco[:n]
    x = reverb(capas_seco, rng)
    # entrada y salida suaves (el vídeo entra y sale de negro)
    ent = np.minimum(1, np.arange(n) / (SR * 1.0)) ** 2
    sal = np.minimum(1, (n - np.arange(n)) / (SR * 0.9)) ** 2
    x *= (ent * sal)[:, None]
    pico = np.max(np.abs(x))
    return x / pico * 0.708                               # pico a -3 dBFS


def guardar(ruta, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duracion", type=float, default=20.0)
    ap.add_argument("--out", default="out/audio/musica.wav")
    ap.add_argument("--semilla", type=int, default=7)
    a = ap.parse_args()
    destino = RAIZ / a.out
    destino.parent.mkdir(parents=True, exist_ok=True)
    x = componer(a.duracion, a.semilla)
    guardar(destino, x)
    print(f"OK {a.out}: {x.shape[0] / SR:.2f} s, {SR} Hz, estéreo, pico {20 * np.log10(np.max(np.abs(x))):.1f} dBFS")


if __name__ == "__main__":
    main()
