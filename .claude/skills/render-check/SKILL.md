---
name: render-check
description: Verifies an output of the studio (video, image, audio, 3D model) before accepting it: extracts frames and LOOKS at them, checks the format with ffprobe, measures the loudness and runs `make verify`. Use it after every render, after changing the audio or after touching the brief.
---

# Verify an output of the studio

The project's golden rule: **never say "done" without having looked at the result.** Automatic tests say whether it works; only looking says whether it looks right
(in this project, `hyperframes check` passed with an arc crossing the text, and the viewer tests would not have detected any of its four visual failures).

## Steps

1. **Video or scene with `seek(t)`**: take 6–8 spread-out frames (not just the first one) into a contact sheet and look at them with Read:
   `node scripts/capture.mjs <scene.html> 1,4,7,10,13,16,19 out/frames/sheet.png 4`
   For an already rendered MP4: `ffmpeg -i out/x.mp4 -vf "fps=1/3,scale=640:-1,tile=3x3" -frames:v 1 out/frames/sheet.png`.
   Look for: cut off or overlapping text, elements out of frame, poor contrast, empty or frozen frames.
2. **Format**: `ffprobe -v error -show_streams -show_format -of json <file>` → 1920x1080, 30 fps, H.264 `yuv420p`, expected duration, AAC 48 kHz audio track.
3. **Audio**: `ffmpeg -i <file> -vn -af ebur128=peak=true -f null -` → integrated −16 LUFS (±1), true peak ≤ −1 dBFS.
   You cannot listen: use a spectrogram (`showspectrumpic`), measurements, and the transcription back with Whisper **large-v3** (`audio/verify_voice.py`).
   NEVER with small Whisper: it invents text in silences and gives a false error of 49–160 %.
4. **Everything together**: `make verify` (or `audio/.venv/bin/python scripts/verify_output.py`). It must end in `ALL CORRECT`.
5. **Report honestly**: what you looked at, what you measured, what you CANNOT judge (naturalness of the voice, taste of the design) and which failures appeared even if you fixed them.

## Known traps
- An "identical" result must be proven (`cmp`, frame hashes with `ffmpeg -f framemd5`), not assumed. Kokoro is not deterministic without a seed.
- Loudness measurements with windows < 0.4 s give −65 LUFS (garbage): they are skipped.
- A PNG can be 10 times slower than JPEG in complex scenes (210 s versus 20 s) and faster in flat scenes.
