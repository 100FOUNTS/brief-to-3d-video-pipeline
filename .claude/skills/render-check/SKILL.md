---
name: render-check
description: Verifica una salida del estudio (vídeo, imagen, audio, modelo 3D) antes de darla por buena: extrae fotogramas y los MIRA, comprueba formato con ffprobe, mide el volumen y ejecuta `make verificar`. Úsala después de cada render, de cambiar el audio o de tocar el brief.
---

# Verificar una salida del estudio

Regla de oro del proyecto: **nunca digas "listo" sin haber mirado el resultado.** Las pruebas automáticas dicen si funciona; solo mirar dice si se ve bien
(en este proyecto, `hyperframes check` pasó con un arco cruzando el texto, y las pruebas del visor no habrían detectado ninguno de sus cuatro fallos visuales).

## Pasos

1. **Vídeo o escena con `seek(t)`**: saca 6–8 fotogramas repartidos (no solo el primero) en una hoja de contactos y míralos con Read:
   `node scripts/capturar.mjs <escena.html> 1,4,7,10,13,16,19 out/frames/hoja.png 4`
   Para un MP4 ya renderizado: `ffmpeg -i out/x.mp4 -vf "fps=1/3,scale=640:-1,tile=3x3" -frames:v 1 out/frames/hoja.png`.
   Busca: texto cortado o solapado, elementos fuera de encuadre, contraste pobre, fotogramas vacíos o congelados.
2. **Formato**: `ffprobe -v error -show_streams -show_format -of json <archivo>` → 1920x1080, 30 fps, H.264 `yuv420p`, duración esperada, pista de audio AAC 48 kHz.
3. **Audio**: `ffmpeg -i <archivo> -vn -af ebur128=peak=true -f null -` → integrado −16 LUFS (±1), pico real ≤ −1 dBFS.
   No puedes oír: usa espectrograma (`showspectrumpic`), medidas, y la transcripción de vuelta con Whisper **large-v3** (`audio/verificar_voz.py`).
   NUNCA con Whisper pequeño: inventa texto en los silencios y da un error falso del 49–160 %.
4. **Todo junto**: `make verificar` (o `audio/.venv/bin/python scripts/verificar_salida.py`). Debe terminar en `TODO CORRECTO`.
5. **Informa con honestidad**: qué miraste, qué medido, qué NO puedes juzgar (naturalidad de la voz, gusto del diseño) y qué fallos aparecieron aunque los hayas corregido.

## Trampas conocidas
- Un resultado "idéntico" hay que demostrarlo (`cmp`, hashes de fotogramas con `ffmpeg -f framemd5`), no suponerlo. Kokoro no es determinista sin semilla.
- Mediciones de loudness con ventanas < 0,4 s dan −65 LUFS (basura): se omiten.
- Un PNG puede ser 10 veces más lento que JPEG en escenas complejas (210 s frente a 20 s) y más rápido en escenas planas.
