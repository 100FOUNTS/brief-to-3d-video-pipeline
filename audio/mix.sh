#!/usr/bin/env bash
# Mezcla voz + música: la música baja cuando habla la voz (sidechain) y todo se normaliza a -16 LUFS / pico real <= -1,5 dB.
# Uso: audio/mix.sh [voz]   (por defecto ef_dora)   ->   out/audio/mezcla_<voz>.wav
set -euo pipefail
cd "$(dirname "$0")/.."
VOZ="${1:-ef_dora}"
ffmpeg -hide_banner -loglevel error -y -i out/audio/musica.wav -i "out/audio/voz_${VOZ}.wav" -filter_complex "
[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,asplit=2[v][vsc];
[0:a]volume=-2dB[m];
[m][vsc]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=450:makeup=1[mduck];
[mduck][v]amix=inputs=2:weights='1 1.7':normalize=0[mix];
[mix]loudnorm=I=-16:TP=-1.5:LRA=7[out]" -map "[out]" -ar 48000 -c:a pcm_s16le "out/audio/mezcla_${VOZ}.wav"
echo "OK out/audio/mezcla_${VOZ}.wav"
