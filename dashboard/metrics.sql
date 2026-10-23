-- Lamp studio metrics, ready to load into a data warehouse (BigQuery, Snowflake, Redshift, ClickHouse, Databricks...).
-- Standard SQL. Generated from docs/metrics.csv by dashboard/build.py. The minutes are ESTIMATES.
CREATE TABLE study_metrics (
  position INTEGER, date VARCHAR(10), phase VARCHAR(20), model VARCHAR(120),
  minutes DOUBLE PRECISION, attempts INTEGER, result VARCHAR(20), notes VARCHAR(2000)
);
INSERT INTO study_metrics (position, date, phase, model, minutes, attempts, result, notes) VALUES
  (1, '2026-10-15', '0', 'qwen3.6:27b (local)', 4.3, 1, 'ok', 'smoke test: script + word-count test; 259 s'),
  (2, '2026-10-15', '0', 'qwen3.6-64k (local)', 4.5, 1, 'ok', 'needle in a haystack with 39578 input tokens: it finds it; 269 s of reading; 17 GB model 100% GPU'),
  (3, '2026-10-15', '1', 'Sonnet 5.5 (cloud)', 25, 2, 'ok', 'scene.html + render.mjs; 8 s 1080p30 in 8.2 s (JPEG) and 7.3 s (PNG); deterministic (0 of 240 frames different). 2 attempts: the 1st came out as yuvj420p'),
  (4, '2026-10-15', '1b', 'Sonnet 5.5 (cloud)', 20, 2, 'ok', 'promo.html: animated 2D lamp (unfolding, light, dust, text); 15 s 1080p30 in 8.3 s of rendering. 2nd attempt: "Articulada" went out of frame at 168 px -> 140 px'),
  (5, '2026-10-15', '2', 'Sonnet 5.5 (cloud)', 50, 3, 'ok', 'HyperFrames: 20 s 1080p30 promo (600 frames) render 16.8 s (27 s with npx); 191 lines vs 237 of the own script. Failures: 2.72:1 contrast on a label; the arc crossed the text'),
  (6, '2026-10-15', '3', 'Sonnet 5.5 (cloud)', 90, 4, 'ok', 'Three.js viewer: 7 parts, exploded view, click, color; 9 Vitest tests (with mutations) + 10 checks in real Chrome. Attempts: 1) PCFSoftShadowMap removed in r186 and favicon 404; 2) small camera when assembled and cropped on mobile; 3) floor with a hill-like edge'),
  (7, '2026-10-15', '3b', 'Sonnet 5.5 (cloud)', 60, 4, 'ok', 'Pure WebGL2: gradient.html + water.html (Fresnel shader + 20 s day-night cycle). render 20 s: JPEG 20.0 s vs PNG 210.5 s (10x). deterministic 0/600. Iterations: regular bands, pill-shaped sun, glints looking like foam'),
  (8, '2026-10-15', '4', 'Sonnet 5.5 (cloud)', 80, 6, 'ok', 'Blender by script (bpy): lamp with pivots, 5 Eevee renders (0.5 s each on Metal) + glb + 120-frame animation in 61.5 s. Failures: light inside the bulb sphere (own shadow), AgX tone desaturates to gray, floor with an edge; my own error with --no-render'),
  (9, '2026-10-15', '4b', 'Sonnet 5.5 (cloud, 2nd instance with MCP)', 25, 2, 'partial', 'Live Blender via MCP: 4 iterative changes looking after each one (42 s); it found a bug of mine (camera at the origin in the saved .blend); visual goal only half met; safe mode blocked an import os'),
  (10, '2026-10-15', '4b-video', 'Sonnet 5.5 (cloud)', 20, 3, 'ok', 'Live-process video: 2nd MCP session with a render after each step (37 s); 26.6 s video assembled with literal captions from the report. Failures: conclusion more optimistic than the report; capture.mjs failed with 1 image'),
  (11, '2026-10-15', '5', 'Sonnet 5.5 (cloud)', 110, 6, 'ok', 'Kokoro-82M voice (ef_dora, em_alex) + numpy music + ffmpeg mix (-16 LUFS, peak -1.5 dB); Whisper large-v3: WER 0-2.4 % (Whisper small hallucinated: 49-161 %). Voice vs music +12 to +19 LU. 2 sentences sped up (1.2x and 1.1x)'),
  (12, '2026-10-15', '5b', 'Sonnet 5.5 (cloud)', 70, 5, 'ok', 'Qwen3-TTS 1.7B CustomVoice 8bit (3.08 GB): WER 0.0 % in the mixes thanks to candidates+Whisper; 5 candidates/sentence; the same sentence 5-9.6 s depending on the seed; speed ignored; ~34 s/voice vs 3.8 s Kokoro'),
  (13, '2026-10-15', '6', 'Sonnet 5.5 (cloud) + Haiku 5.5 (hooks/skill/agent tests)', 180, 6, 'ok', 'make studio from scratch: 24 s (Arco) and 29 s (Brasa), 20/20 checks; pieces in parallel (viewer 1 s, blender 4 s, audio 5 s, video 23-28 s); regression: 600 identical frames; 2nd brief without touching code; hooks block editing generated files (real test)'),
  (14, '2026-10-15', '7', 'Qwen3.6 27B (local, via Claude Code)', 8.2, 1, 'ok', 'Controlled Phase 1 experiment (video as code): 14/14 prompt requirements, 1/2 extra quality (yuvj420p); 494 s, 8 turns, 196k input tokens; the golden line strikes through the text and it did not notice'),
  (15, '2026-10-15', '7', 'Sonnet 5.5 (cloud, via Claude Code)', 1.2, 1, 'ok', 'Same experiment: 14/14 requirements and 2/2 quality; 72 s, 25 turns; theoretical cost 0.26 USD (with Pro it is quota); more careful design'),
  (16, '2026-10-15', '7c', 'Sonnet 5.5 (cloud)', 60, 3, 'ok', 'Load the Blender .glb in the viewer: lampFromGLTF (attach to the root), model selector, 18 Vitest tests (9 new, 3 mutations), 16 checks in Chrome. Failures: spotlight mis-aimed in the glb (inherited rotation); my test measured it in local coordinates and did not see it');

-- The queries of each chart in the local dashboard (dashboard/index.html), over the study_metrics table:
-- 1) Minutes per phase (estimated)
SELECT phase, SUM(minutes) AS study_metricsinutes FROM study_metrics GROUP BY phase ORDER BY MIN(position);
-- 2) Attempts until accepted, per phase
SELECT phase, SUM(attempts) AS attempts FROM study_metrics GROUP BY phase ORDER BY MIN(position);
-- 3) Result of each phase
SELECT result, COUNT(*) AS phases FROM study_metrics GROUP BY result;
-- 4) Cumulative effort (minutes) over the exercise
SELECT phase,        SUM(minutes) OVER (ORDER BY position) AS cumulative_minutes FROM study_metrics ORDER BY position;
