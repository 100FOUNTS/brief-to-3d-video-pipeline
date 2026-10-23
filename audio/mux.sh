#!/usr/bin/env bash
# Attaches the mix to the video without re-encoding the picture: out/promo-hyperframes-sound-<voice>.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
VOICE="${1:-em_alex}"
ffmpeg -hide_banner -loglevel error -y -i out/promo-hyperframes.mp4 -i "out/audio/mix_${VOICE}.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "out/promo-hyperframes-sound-${VOICE}.mp4"
echo "OK out/promo-hyperframes-sound-${VOICE}.mp4"
