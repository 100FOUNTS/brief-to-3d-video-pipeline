# Estudio creativo de la lámpara

Mini-estudio local: desde UN archivo (`brief.json`) produce un modelo 3D de lámpara, un visor web, un vídeo promocional de 20 s con voz y música, y comprueba el resultado.
El plan y la investigación están en `../proyectos-avanzados-ia-2026/`. El historial de lo que salió bien y mal, en `docs/diario.md` y `docs/metricas.csv`.

## Cómo se usa

- `make studio` (o `make -j4 studio`): TODO desde `brief.json`; termina con `make verificar` (20 comprobaciones). `BRIEF=otro.json` usa otro brief.
- `make variante N=frio B=brief.frio.json`: lo mismo en un `git worktree` aparte (`../estudio-lampara-frio`), sin pisar este.
- Piezas sueltas: `make blender | viewer | hyperframes | audio`. Ayuda: `make help`.

## Reglas

- **`brief.json` es la única fuente** de nombre, lema, beneficios, guion de la voz, paleta, música y voz. Tras editarlo: `make generar`.
- **Archivos GENERADOS (no se editan a mano):** `hyperframes/promo/index.html`, `docs/guion.json`, `viewer/src/brief.generated.js`.
  La plantilla del vídeo es `plantillas/hyperframes-promo.template.html` (fuera de `hyperframes/promo/`: si no, `hyperframes check` falla por dos composiciones raíz).
- **Lo que el brief NO puede cambiar:** la geometría de la lámpara, las 5 escenas y los 20 s de duración. Otro producto distinto de una lámpara exige código nuevo.
- Nunca digas "listo" sin MIRAR el resultado (hoja de contactos, `ffprobe`, `make verificar`). Usa la skill `render-check`.
- Todo lo que dependa del tiempo (vídeo, shaders) debe ser función de `t`: sin `Date`, `requestAnimationFrame`, `setTimeout` ni `Math.random` en lo que se renderiza.
- Cambios pequeños; si una tarea toca más de 5 archivos, primero un plan. Registra fallos no obvios en `docs/diario.md` y una fila por intento en `docs/metricas.csv`.
- Solo se escribe dentro de esta carpeta (lo exige un hook).

## Herramientas

Node 22, ffmpeg, Blender 5.2.2 (`/Applications/Blender.app`), Chrome, Ollama; Python del proyecto en `audio/.venv` (Kokoro, Whisper large-v3). Sin instalaciones globales ni de pago sin avisar.

## Piezas de Claude Code de este proyecto (`.claude/`)

- Skill `render-check`: cómo verificar una salida.
- Subagentes: `modelador` (Blender), `web3d` (visor Three.js), `video` (HyperFrames), `audio` (voz, música, mezcla). Cada uno lleva lo aprendido en su área.
- Hooks (`.claude/settings.json`): `guardia-ruta.py` bloquea escribir fuera del proyecto y editar archivos generados; `despues-de-editar.py` regenera/valida tras editar el brief o la plantilla.
  Son barandillas, NO seguridad: solo vigilan las herramientas Write y Edit; un comando de Bash puede saltárselas.

## Estructura

`brief.json` · `plantillas/` · `scripts/` (generador, verificador, variantes, capturas) · `video/` (Fases 1) · `hyperframes/promo/` (Fase 2) · `viewer/` (Fase 3) · `webgl/` (Fase 3b) · `blender/` (Fase 4) · `audio/` (Fase 5) · `out/` (resultados, no se versiona)
