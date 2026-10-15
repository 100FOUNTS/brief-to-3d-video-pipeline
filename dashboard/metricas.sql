-- Métricas del estudio de la lámpara, listas para cargar en un almacén de datos (BigQuery, Snowflake, Redshift, ClickHouse, Databricks...).
-- SQL estándar. Generado desde docs/metricas.csv por dashboard/exportar_sql.py. Los minutos son ESTIMACIONES.
CREATE TABLE metricas_estudio (
  orden INTEGER, fecha VARCHAR(10), fase VARCHAR(20), modelo VARCHAR(120),
  minutos DOUBLE PRECISION, intentos INTEGER, resultado VARCHAR(20), notas VARCHAR(2000)
);
INSERT INTO metricas_estudio (orden, fecha, fase, modelo, minutos, intentos, resultado, notas) VALUES
  (1, '2026-10-15', '0', 'qwen3.6:27b (local)', 4.3, 1, 'ok', 'prueba de humo: script + test de conteo de palabras; 259 s'),
  (2, '2026-10-15', '0', 'qwen3.6-64k (local)', 4.5, 1, 'ok', 'aguja en pajar con 39578 tokens de entrada: acierta; 269 s de lectura; modelo 17 GB 100% GPU'),
  (3, '2026-10-15', '1', 'Sonnet 5.5 (nube)', 25, 2, 'ok', 'scene.html + render.mjs; 8 s 1080p30 en 8.2 s (JPEG) y 7.3 s (PNG); determinista (0 de 240 fotogramas distintos). 2 intentos: el 1º salio en yuvj420p'),
  (4, '2026-10-15', '1b', 'Sonnet 5.5 (nube)', 20, 2, 'ok', 'promo.html: lampara 2D animada (despliegue, luz, polvo, texto); 15 s 1080p30 en 8.3 s de render. 2o intento: "Articulada" se salia del encuadre a 168 px -> 140 px'),
  (5, '2026-10-15', '2', 'Sonnet 5.5 (nube)', 50, 3, 'ok', 'HyperFrames: promo 20 s 1080p30 (600 fotogramas) render 16.8 s (27 s con npx); 191 lineas vs 237 del script propio. Fallos: contraste 2.72:1 en etiqueta; arco cruzaba el texto'),
  (6, '2026-10-15', '3', 'Sonnet 5.5 (nube)', 90, 4, 'ok', 'Visor Three.js: 7 piezas, vista explosionada, clic, color; 9 pruebas Vitest (con mutaciones) + 10 comprobaciones en Chrome real. Intentos: 1) PCFSoftShadowMap eliminado en r186 y favicon 404; 2) camara pequena armada y movil recortado; 3) suelo con borde de colina'),
  (7, '2026-10-15', '3b', 'Sonnet 5.5 (nube)', 60, 4, 'ok', 'WebGL2 puro: gradiente.html + agua.html (shader Fresnel+ciclo dia-noche 20 s). render 20 s: JPEG 20.0 s vs PNG 210.5 s (10x). determinista 0/600. Iteraciones: bandas regulares, sol en pildora, destellos como espuma'),
  (8, '2026-10-15', '4', 'Sonnet 5.5 (nube)', 80, 6, 'ok', 'Blender por script (bpy): lampara con pivotes, 5 renders Eevee (0.5 s c/u en Metal) + glb + animacion 120 fotogramas en 61.5 s. Fallos: luz dentro de la esfera de la bombilla (sombra propia), tono AgX desatura a gris, suelo con borde; error mio con --sin-render'),
  (9, '2026-10-15', '4b', 'Sonnet 5.5 (nube, 2a instancia con MCP)', 25, 2, 'parcial', 'Blender en vivo por MCP: 4 cambios iterativos mirando tras cada uno (42 s); encontro un bug mio (camara en el origen en el .blend guardado); objetivo visual cumplido a medias; modo seguro bloqueo un import os'),
  (10, '2026-10-15', '4b-video', 'Sonnet 5.5 (nube)', 20, 3, 'ok', 'Video del proceso en vivo: 2a sesion MCP con render tras cada paso (37 s); video 26.6 s montado con rotulos literales del informe. Fallos: conclusion mas optimista que el informe; capturar.mjs fallaba con 1 imagen'),
  (11, '2026-10-15', '5', 'Sonnet 5.5 (nube)', 110, 6, 'ok', 'Voz Kokoro-82M (ef_dora, em_alex) + musica numpy + mezcla ffmpeg (-16 LUFS, pico -1.5 dB); Whisper large-v3: WER 0-2.4 % (Whisper small alucinaba: 49-161 %). Voz vs musica +12 a +19 LU. 2 frases aceleradas (1.2x y 1.1x)'),
  (12, '2026-10-15', '5b', 'Sonnet 5.5 (nube)', 70, 5, 'ok', 'Qwen3-TTS 1.7B CustomVoice 8bit (3.08 GB): WER 0.0 % en las mezclas gracias a candidatas+Whisper; 5 candidatas/frase; misma frase 5-9.6 s segun semilla; speed ignorado; ~34 s/voz vs 3.8 s Kokoro'),
  (13, '2026-10-15', '6', 'Sonnet 5.5 (nube) + Haiku 5.5 (pruebas de hooks/skill/agente)', 180, 6, 'ok', 'make studio desde cero: 24 s (Arco) y 29 s (Brasa), 20/20 comprobaciones; piezas en paralelo (visor 1 s, blender 4 s, audio 5 s, video 23-28 s); regresion: 600 fotogramas identicos; 2o brief sin tocar codigo; hooks bloquean edicion de generados (prueba real)'),
  (14, '2026-10-15', '7', 'Qwen3.6 27B (local, vía Claude Code)', 8.2, 1, 'ok', 'Experimento controlado Fase 1 (video por codigo): 14/14 requisitos del prompt, 1/2 calidad extra (yuvj420p); 494 s, 8 turnos, 196k tokens de entrada; la linea dorada tacha el texto y no lo noto'),
  (15, '2026-10-15', '7', 'Sonnet 5.5 (nube, vía Claude Code)', 1.2, 1, 'ok', 'Mismo experimento: 14/14 requisitos y 2/2 calidad; 72 s, 25 turnos; coste teorico 0.26 USD (con Pro es cuota); diseno mas cuidado');

-- Las consultas de cada gráfico del dashboard local (dashboard/index.html), sobre la tabla metricas_estudio:
-- 1) Minutos por fase
SELECT fase, SUM(minutos) AS minutos FROM metricas_estudio GROUP BY fase ORDER BY MIN(orden);
-- 2) Intentos por fase
SELECT fase, SUM(intentos) AS intentos FROM metricas_estudio GROUP BY fase ORDER BY MIN(orden);
-- 3) Resultado de cada fase
SELECT resultado, COUNT(*) AS fases FROM metricas_estudio GROUP BY resultado;
-- 4) Esfuerzo acumulado
SELECT fase, SUM(minutos) OVER (ORDER BY orden) AS minutos_acumulados FROM metricas_estudio ORDER BY orden;
