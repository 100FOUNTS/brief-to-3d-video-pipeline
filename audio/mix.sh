#!/usr/bin/env bash
# Mixes voice + music: the music ducks when the voice speaks (sidechain) and everything is normalized to -16 LUFS / true peak <= -1.5 dB.
# Usage: audio/mix.sh [voice]   (default em_alex)   ->   out/audio/mix_<voice>.wav
set -euo pipefail
cd "$(dirname "$0")/.."
VOICE="${1:-em_alex}"
ffmpeg -hide_banner -loglevel error -y -i out/audio/music.wav -i "out/audio/voice_${VOICE}.wav" -filter_complex "
[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,asplit=2[v][vsc];
[0:a]volume=-2dB[m];
[m][vsc]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=450:makeup=1[mduck];
[mduck][v]amix=inputs=2:weights='1 1.7':normalize=0[mix];
[mix]loudnorm=I=-16:TP=-1.5:LRA=7[out]" -map "[out]" -ar 48000 -c:a pcm_s16le "out/audio/mix_${VOICE}.wav"
echo "OK out/audio/mix_${VOICE}.wav"
