# Estudio lámpara

Producto original: lámpara de escritorio articulada "Arco". Prohibido copiar marcas, personajes o música existentes.
El plan completo está en `../proyectos-avanzados-ia-2026/PLAN-EJERCICIO.md`. El brief está en `brief.md`.

## Reglas

- Todo se ejecuta con `make`. No dejes pasos manuales.
- Después de generar una imagen, un vídeo o un modelo, MÍRALO (extrae fotogramas con ffmpeg) antes de decir que está listo.
- Vídeo: 1920x1080, 30 fps. Paleta y tipografía en `brief.md`.
- Cambios pequeños. Si una tarea necesita más de 5 archivos, primero escribe un plan y espera confirmación.
- Todo lo que dependa del tiempo (vídeo, shaders) debe ser función de `t`: nada de `Date`, `requestAnimationFrame` ni `setTimeout` en las escenas que se renderizan.
- Resultados en `out/` (no se versiona). Código fuente solo en su carpeta de fase.
- Registra en `docs/diario.md` cada fallo no obvio y en `docs/metricas.csv` una fila por intento.

## Herramientas disponibles

Node 22, npm, ffmpeg, Python 3 con `uv`, Blender (`blender -b -P script.py`), Google Chrome, Ollama.
No instales programas de pago ni dependencias globales sin avisar.

## Estructura

`video/` Fase 1 · `hyperframes/` Fase 2 · `viewer/` Fase 3 · `webgl/` Fase 3b · `blender/` Fase 4 · `audio/` Fase 5 · `dashboard/` Fase 7b
