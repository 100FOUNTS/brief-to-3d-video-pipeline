# Diario del ejercicio

Una entrada por sesión: qué pediste, qué salió mal, cuánto tardó, qué aprendiste.

## 2026-10-15 · Fase 0
- Inicio del ejercicio. Mac M4 Max, 36 GB.
- Prueba de humo con qwen3.6:27b local: 259 s, 1 intento, script y prueba correctos. Aviso: Claude Code no reconoce el modelo y asume ventana de 200k; con ANTHROPIC_API_KEY definido se desactivan los conectores de claude.ai (solo en esa sesión).
- Contexto: el servidor de Ollama carga qwen3.6:27b con 32768 por defecto (la mitad de lo recomendado). Creé la variante `qwen3.6-64k` (`ollama/Modelfile.qwen3.6-64k`) con num_ctx 65536. Carga en 17 GB, 100% GPU.
- Prueba de aguja en pajar con 39.578 tokens: acierta el dato escondido, pero la lectura tarda 269 s (unos 147 tokens/s). Consecuencia: cada sesión nueva de Claude Code cuesta minutos al arrancar; conviene sesiones largas y `CLAUDE.md` corto.
- Lanzador: `./scripts/claude-local.sh` (usa el modelo local sin tocar la configuración global).
- Memoria libre tras cargar el modelo: unos 2 GB. Cierra apps pesadas antes de renderizar con Blender.

## 2026-10-15 · Fase 1 (hecha con Sonnet 5.5, no con el modelo local)
- Resultado: `video/scene.html`, `video/render.mjs`, `make video` -> `out/titulo.mp4` (1920x1080, 30 fps, 240 fotogramas, 8 s).
- Fallo 1: el primer MP4 salió en `yuvj420p` (rango completo), porque las capturas JPEG entran como "JPEG range". Se arregla en el filtro de FFmpeg (`scale=in_range=full:out_range=limited,format=yuv420p`) y marcando bt709/tv. Sin esto algunos reproductores muestran colores apagados.
- Verificación visual: 0 s = solo fondo, 1 s = título a medio fundido y la línea sin empezar, 4 s = todo completo.
- Determinismo: dos renders -> mismos hashes de los 240 fotogramas La prueba no es vacía: dentro de un mismo render hay 96 hashes distintos de 240, que es lo esperable (los fotogramas de reposo antes de 0,5 s y después de 3 s son idénticos).
- Sorpresa: PNG (7.3 s) resultó MÁS rápido que JPEG (8.2 s), al revés que en el documento (26 s vs 11,5 s). La escena es casi plana y el PNG la comprime muy bien; con escenas complejas (3D, shaders) probablemente se invierta. Re-medir en la Fase 3b.

## 2026-10-15 · Fase 1b: escena con contenido (`video/promo.html`)
- Motivo: la escena de la Fase 1 (palabra + línea) probaba el método pero no enseñaba su potencial. Hice una de 15 s con la misma `seek(t)`: lámpara dibujada en Canvas 2D que se despliega con rebote, se enciende con parpadeo, cono de luz con partículas de polvo, giro de pose ("articulada"), cambio de color a dorado ("luz cálida") y textos por escenas.
- Técnicas: easing (smoothstep, outBack), hash determinista (`Math.sin`) en lugar de `Math.random` para el polvo y el parpadeo, composición `screen` para la luz, recorte (`clip`) al cono.
- Fallo: a 168 px la palabra "Articulada" medía unos 950 px y se salía por el borde derecho (x=1010 + 950 > 1920). Se vio en la hoja de contactos; a 140 px cabe.
- Render: 450 fotogramas en 8,3 s.

## 2026-10-15 · Fase 2: HyperFrames (hecha con Sonnet 5.5)
- Setup: las skills de HyperFrames ya estaban en `~/.claude/skills`; `npx hyperframes skills update general-video` instaló 11 skills y las enlazó en otros 4 directorios de agentes (efecto fuera del proyecto). No hizo falta instalar el plugin.
- Proyecto: `hyperframes/promo/` (BRIEF.md + index.html). Concepto: la luz es la narradora; un arco se dibuja y la luz viaja por él mientras aparece cada beneficio. Montserrat 900 + IBM Plex Mono.
- `check` pasó a la primera con 0 errores y 6 avisos de estructura (5 escenas en un solo archivo: HyperFrames recomienda sub-composiciones desde 3 cortes duros). Lo dejé así por alcance; queda como mejora.
- Fallo 1 (contraste): etiqueta "03 / 03" en #ffb703 sobre el brillo dorado: 2,72:1 (pide 3:1). Cambié las etiquetas a #ffc532.
- Fallo 2 (diseño, NO lo detecta `check`): el arco cruzaba las letras y la etiqueta caía sobre la línea. Solución: arco a 32% de opacidad tras dibujarse, bloque de texto 140 px más abajo, quitar la línea del suelo. Lección: `check` garantiza que funciona, no que se vea bien; hay que mirar la hoja de contactos.
- Render: 600 fotogramas, 20 s, 16,8 s (captura 8,2 s, codificación 2,4 s), GPU por hardware (Metal). 4 workers.
- Fuentes: el compilador descargó Montserrat e IBM Plex Mono de Google Fonts en el primer build y las guardó en caché, aunque la documentación dice que vienen incluidas.
- Telemetría de HyperFrames: ACTIVADA por defecto (`~/.hyperframes/config.json`). Se desactiva con `npx hyperframes telemetry disable`.
