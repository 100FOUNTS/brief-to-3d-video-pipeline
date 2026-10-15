# Retrospectiva del ejercicio (15 de octubre de 2026)

Un día de trabajo, 15 intentos registrados, unos 750 minutos estimados. Qué salió, qué aprendí y qué cambiaría. Los datos están en `docs/diario.md`,
`docs/metricas.csv` y `dashboard/index.html`. Los minutos son estimaciones; casi todo lo hizo Sonnet 5.5 en la nube (el plan decía que el modelo local).

## Lo que se construyó
Desde `brief.json`, `make studio` produce en ~25 s: un vídeo de 20 s con voz y música, un modelo 3D de lámpara (.glb), un visor web con vista explosionada,
5 renders de Blender, y 20 comprobaciones automáticas. Se probó con dos productos distintos (Arco, Brasa) sin tocar código.

## Qué funcionó
- **Verificar mirando, no solo con pruebas.** Casi todos los fallos importantes los encontró una hoja de contactos o una medición, no una prueba que pasara.
- **Probar el verificador.** Con casos negativos (mutantes) detecté tres veces que una comprobación no comprobaba nada (el medidor de reloj en el evaluador, el contraste, un `cmp` ignorado).
- **Probar desde cero** (`git worktree` limpio): encontró el fallo que habría roto el proyecto (`multiple_root_compositions`).
- **Una sola fuente de verdad** (`brief.json`) con un generador que valida y regenera: el segundo producto salió sin código nuevo.
- **Documentar los fallos** en el diario evitó repetirlos y alimentó los subagentes.

## Lecciones técnicas que no estaban en el documento original
1. El formato de color de un MP4 hecho de JPEG sale `yuvj420p` y se ve apagado en algunos reproductores; hay que forzar `yuv420p`/bt709.
2. PNG frente a JPEG depende de la escena: 7,3 s frente a 8,2 s en una escena plana, 210 s frente a 20 s en un shader.
3. Kokoro no es determinista sin semilla; con `mx.random.seed` queda reproducible hasta el redondeo.
4. Whisper pequeño alucina texto en los silencios (error falso del 49–160 %); con Whisper large-v3, 0–2,4 %. Desconfía de la métrica antes que del audio.
5. En Qwen3-TTS (mlx-audio) el parámetro `speed` se ignora y el ritmo varía de 5 a 9,6 s por la misma frase; Kokoro suena más natural en español (decisión del usuario, a oído).
6. Borrar un modelo del caché de Hugging Face no libera espacio: hay que borrar los blobs huérfanos.
7. Blender 5.2: único motor `BLENDER_EEVEE`; la luz dentro de una esfera opaca queda tapada por la propia sombra; AgX desatura los brillos fuertes.
8. El servidor MCP de Blender no tiene contraseña y el modo seguro solo protege el camino del MCP.
9. Los hooks de Claude Code solo vigilan las herramientas que se les indican; un comando de Bash los salta.

## Modelos: qué usar para qué (con la confianza que dan los datos)
Experimento controlado: misma tarea (la Fase 1), mismo prompt, mismo evaluador automático, **un intento por modelo**.

| | Qwen3.6 27B local | Sonnet 5.5 nube |
| --- | --- | --- |
| Requisitos del prompt | 14/14 | 14/14 |
| Calidad no pedida | 1/2 (yuvj420p) | 2/2 |
| Tiempo | 494 s | 72–78 s |
| Turnos | 8 | 25 |
| Diseño | línea dorada tacha el texto; no lo notó | más cuidado (subrayado, curva suave) |

- **Confianza alta:** el modelo local resuelve una tarea acotada, bien especificada y verificable, y es ~6–7 veces más lento.
- **Confianza media:** en esa tarea Sonnet es más cuidadoso con detalles que nadie pidió. Un solo intento por modelo: no hay estadística.
- **No probado:** tareas grandes y de varios archivos con el modelo local (Blender, el visor, el generador del brief) y Opus 5.5. No sé si el local las aguantaría; no lo afirmo.
- Mi recomendación provisional: modelo local para tareas pequeñas y bien definidas (cuando el tiempo no importa o no quieres gastar cuota); Sonnet para lo que cruza varios archivos o exige criterio visual.

## Mis errores recurrentes (para no repetirlos)
- Afirmar algo que no había comprobado (que Kokoro era idéntico entre ejecuciones; las cifras de tamaño de un modelo; "no hay fallos" con una comprobación que no miraba).
- Umbrales arbitrarios sacados de mi propia solución (en el evaluador del experimento, que suspendía una solución correcta).
- Gráficos que sugieren conclusiones falsas (el de "minutos por intento según el modelo", ya eliminado).
- Lanzar trabajo que consume cuota (repetir Sonnet en el experimento) sin explicarlo antes.

## Qué haría ahora
1. Repetir el experimento 3–5 veces por modelo y con una tarea mayor (p. ej. el generador del brief) antes de sacar conclusiones.
2. Probar Opus 5.5 y el modelo local en una tarea de varios archivos; medir cuota y tiempo.
3. Cargar el .glb de Blender en el visor (pendiente) y ampliar `make studio` con las capturas del visor.
4. Hacer que `verificar` incluya una revisión visual asistida (hoja de contactos que se guarda siempre).
