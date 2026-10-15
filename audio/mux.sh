#!/usr/bin/env bash
# Pega la mezcla al vídeo sin recodificar la imagen: out/promo-hyperframes-sonido-<voz>.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
VOZ="${1:-em_alex}"
ffmpeg -hide_banner -loglevel error -y -i out/promo-hyperframes.mp4 -i "out/audio/mezcla_${VOZ}.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "out/promo-hyperframes-sonido-${VOZ}.mp4"
echo "OK out/promo-hyperframes-sonido-${VOZ}.mp4"
