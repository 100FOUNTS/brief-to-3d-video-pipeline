# Inventario: todo lo usado en el ejercicio

Recogido el 15 de octubre de 2026 desde el propio equipo (versiones leídas con los comandos, no de memoria). Donde una **licencia** no la comprobé hoy, lo digo.

## 1. Equipo
| | |
| --- | --- |
| Equipo | Mac con chip Apple M4 Max, 36 GB de memoria unificada |
| Sistema | macOS 26.6.2 (Darwin 25.6.0) |
| Disco | `out/` 197 MB; caché de Hugging Face 24 GB (16 GB son un modelo de código que ya tenías) |

## 2. Modelos de IA
| Modelo | Para qué se usó | Dónde corre | Peso | Licencia |
| --- | --- | --- | --- | --- |
| **Claude Sonnet 5.5** | Casi todo el ejercicio (código, diseño, análisis) y el dashboard en claude.ai | Nube, plan Pro | n/d | Servicio de Anthropic |
| Claude Haiku 5.5 | Pruebas de hooks, skill y subagente (instancias reales de Claude Code) | Nube, plan Pro | n/d | Servicio |
| **Qwen3.6 27B** (variante `qwen3.6-64k`, contexto de 64K) | Prueba de humo (Fase 0) y experimento controlado (Fase 7) | Local, Ollama | 17 GB | No la verifiqué (la página de Ollama no la indica) |
| **Kokoro-82M** (bf16, MLX) | La **voz** del vídeo (`em_alex`) | Local, GPU del Mac | 0,39 GB | Apache 2.0 (ficha de Hugging Face) |
| **Whisper large-v3** (fp16, MLX) | Verificar que la voz se entiende (transcribir de vuelta) | Local | 3,09 GB | No figura en la ficha; no la verifiqué |
| Qwen3-TTS 1.7B, Whisper pequeño | Probados y **descartados** (borrados) | Local | ≈4 GB | Qwen3-TTS: Apache 2.0 (ficha) |
| No usados | `gemma4:12b`, `qwen3.5:4b`, `qwen3:4b`, `granite4.2:3b`, `mxbai-embed-large` (ya estaban instalados) | | | |

Opus 5.5 y GPT-6 Astra **no** se usaron.

## 3. Programas y entornos de ejecución
| Programa | Versión | Para qué |
| --- | --- | --- |
| Claude Code | 2.1.300 | El entorno de trabajo de todo el ejercicio |
| Node.js / npm | 22.23.1 / 10.9.8 | Render de vídeo, visor, pruebas |
| Python (sistema / proyecto) | 3.14.6 / 3.12.15 (entorno `audio/.venv`) | Scripts, voz, música, dashboard |
| uv | 0.13.1 | Entornos de Python y servidor MCP |
| FFmpeg | 8.1.2 | Unir fotogramas, mezclar audio, medir volumen, extraer imágenes |
| Blender | 5.2.2 LTS | Modelo 3D y renders, por código (`bpy`) |
| Google Chrome | 155.0.8059.79 | Navegador sin ventana para renderizar y verificar |
| Ollama | 0.30.11 | Servir el modelo local |
| git / GNU Make | 2.55.0 / 3.81 | Control de versiones, `git worktree`, orquestación (`make -j4`) |
| Homebrew, zsh | | Instalar `uv` y Blender |

## 4. Librerías
**JavaScript**
| Librería | Versión | Uso | Licencia |
| --- | --- | --- | --- |
| three | 0.186.1 | Visor 3D (con OrbitControls, RoomEnvironment, RoundedBoxGeometry, GLTFLoader) | MIT (npm) |
| vite / vitest | 8.3.4 / 5.0.4 | Servidor y empaquetado / pruebas | no verificada hoy |
| playwright-core | 1.64.1 | Controlar Chrome sin ventana (render y verificación) | no verificada hoy |
| chart.js | 4.5.1 | Gráficos del dashboard | MIT (npm) |
| HyperFrames CLI | 0.8.161 (fijada) | Vídeo desde HTML | Apache 2.0 (repositorio) |
| GSAP | 3.14.2 (CDN) | Animación del vídeo de HyperFrames | no verificada hoy |

**Python (`audio/.venv`)**: mlx 0.32.4, mlx-audio 0.5.9 (MIT, PyPI), misaki 0.9.4 (Apache 2.0), espeakng-loader 0.2.4, phonemizer-fork 3.3.2, numpy 2.5.4, transformers 5.19.0, huggingface-hub 2.2.0, SQLite 3.53.1 (de la biblioteca estándar).
**Dentro de Blender**: `bpy` y `bmesh`. **Complemento**: mcp-for-blender 2.1.9 (MIT, PyPI), instalado pero **no activado** de forma permanente.

## 5. Formatos, estándares y técnicas
- **Gráficos:** WebGL (vía Three.js), **WebGL2 puro** y shaders GLSL ES 3.00 (agua con Fresnel), glTF/GLB 2.0, materiales PBR (Principled BSDF), modificadores de bisel y solidificado, motor Eevee (Metal).
- **Vídeo:** H.264 `yuv420p` con rango limitado y bt709, 1920x1080 a 30 fps; vídeo como función del tiempo `seek(t)` (determinista).
- **Audio:** WAV PCM, AAC a 48 kHz, sidechain (ducking), normalización a −16 LUFS con pico real ≤ −1,5 dB (EBU R128 con `ebur128`).
- **Ingeniería:** pruebas unitarias y **mutación** (romper a propósito), verificación en navegador real, semillas fijas para reproducibilidad, un brief único como fuente de datos, plantillas, `git worktree`, paralelismo con `make -j4`, SQL (consultas con funciones de ventana), CSV.
- **Protocolo/IA:** MCP (Model Context Protocol), uso de herramientas, instancias anidadas de Claude Code (`claude -p`), experimento controlado con evaluador automático.

## 6. Servicios y cuentas
- **claude.ai, plan Pro**: modelos de Claude, Claude Code, y Claude Dashboards (beta, plantilla Dashboard).
- **Hugging Face Hub** (descargas sin token), **npm**, **PyPI**, **Homebrew**, registro de Ollama, **Google Fonts** (el primer build de HyperFrames bajó Montserrat e IBM Plex Mono) y **jsDelivr** (carga GSAP).
- Extensión **Claude in Chrome** (conectada por el autor).
- **No se usó**: GitHub (el conector falló y no se subió nada), ninguna API de pago, ningún servicio de render ni de voz en la nube.

## 7. Piezas de Claude Code del proyecto (`.claude/`)
- **1 skill** (`render-check`) y **4 subagentes** (`modelador`, `web3d`, `video`, `audio`), con lo aprendido en cada área.
- **2 hooks** (`guardia-ruta.py`, `despues-de-editar.py`). Solo vigilan Write y Edit; un comando de Bash los salta.
- Instaladas por la herramienta de HyperFrames fuera del proyecto: **11 skills** en `~/.claude/skills` (y enlazadas en otros 4 directorios de agentes).

## 8. Lo construido (por fase)
| Fase | Resultado |
| --- | --- |
| 0 | Entorno, `CLAUDE.md`, modelo local con 64K de contexto |
| 1, 1b | Vídeo por código con `seek(t)`: título (8 s) y lámpara dibujada en Canvas 2D (15 s) |
| 2 | Promo de 20 s con HyperFrames |
| 3, 3b | Visor 3D con Three.js (vista explosionada); shader de agua en WebGL2 puro |
| 4, 4b | Lámpara en Blender por script (5 renders, animación, `.glb`) y en vivo por MCP |
| 5, 5b | Voz (Kokoro), música sintetizada, mezcla y verificación; prueba de Qwen3-TTS |
| 6 | `make studio` desde `brief.json`, verificador de 21 comprobaciones, skill, subagentes, hooks, variantes en worktrees |
| 7, 7b | Experimento local frente a Sonnet, retrospectiva, dashboard local y en claude.ai |
| Extra | `.glb` de Blender cargado en el visor con selector de modelo |

**Cifras:** 24 commits, 83 archivos versionados, ≈4.600 líneas (Python 1.365, HTML 1.198, JS 745 + 232 de `.mjs`, Markdown 662, JSON 225, shell 130, CSS 77), 22 objetivos de `make`.

## 9. Dinero gastado
**Nada fuera del plan Pro de claude.ai** (20 USD al mes, 17 si es anual, según la [página de precios de Anthropic](https://claude.com/pricing)). Todo lo demás es gratuito o corrió en el Mac del autor. El uso de Claude consumió cuota del plan, no se facturó por separado. (Claude Code informa un coste «equivalente en API» por sesión, que es teórico con Pro y sin sentido para el modelo local.)

## 10. Cambios hechos FUERA de la carpeta del proyecto
Para poder reproducir el entorno, esto es lo que se tocó:
- Instalados con Homebrew: `uv` y Blender (versión de cask).
- `~/.claude/skills/` y otros 4 directorios de agentes: 11 skills de HyperFrames.
- `~/.hyperframes/`: configuración de HyperFrames, con la **telemetría activada** (se apaga con `npx hyperframes telemetry disable`).
- `~/Library/Application Support/Blender/5.2/scripts/addons/blender_mcp.py`: el complemento MCP, **sin activar**.
- `~/.cache/huggingface/`: Kokoro y Whisper large-v3 (los de Qwen3-TTS y Whisper pequeño se borraron).
- `~/.ollama`: el modelo `qwen3.6:27b` y su variante de 64K.
- `experimento-fase7/`: carpetas del experimento (incluidas en este repositorio, sin `node_modules` ni `out/`).
- En la cuenta de claude.ai del autor: un chat y un dashboard privados («Dashboard de métricas CSV»).
- Procesos que quedan abiertos: el servidor del visor en `localhost:5173` (se detiene con Ctrl+C).
