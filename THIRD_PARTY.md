# Componentes de terceros y sus licencias

Este repositorio es MIT (ver `LICENSE`). **No redistribuye modelos ni programas de terceros**, con una excepción: `dashboard/chart.umd.js` (Chart.js, MIT, con su aviso de licencia dentro del archivo). Todo lo demás se descarga o instala al preparar el entorno.

**Fuente de cada dato:** `registro` = campo de licencia del registro oficial (npm o PyPI) consultado el 23 de octubre de 2026 · `ficha HF` = metadatos de la ficha del modelo en Hugging Face, misma fecha · `conocimiento general` = no lo verifiqué hoy; compruébalo antes de un uso comercial.

## Bibliotecas de JavaScript
| Componente | Versión usada | Licencia | Fuente |
| --- | --- | --- | --- |
| three | 0.186.1 | MIT | registro |
| vite | 8.3.x | MIT | registro |
| vitest | 5.0.x | MIT | registro |
| playwright-core | 1.64.1 | Apache-2.0 | registro |
| chart.js (archivo incluido) | 4.5.1 | MIT | encabezado del propio archivo |
| HyperFrames (CLI) | 0.8.161 | Apache-2.0 | registro |
| GSAP (se carga desde jsDelivr, no se incluye) | 3.14.2 | «Standard "no charge" license» de GSAP: **no es una licencia de código abierto**; léela en gsap.com/standard-license antes de un uso comercial | registro |

## Bibliotecas de Python (`audio/requirements.txt`)
| Componente | Versión | Licencia | Fuente |
| --- | --- | --- | --- |
| mlx | 0.32.4 | MIT | registro |
| mlx-audio | 0.5.9 | MIT | registro |
| misaki | 0.9.4 | Apache | registro |
| numpy | 2.5.4 | BSD-3-Clause (más componentes permisivos) | registro |
| scipy | 1.18.1 | BSD (el campo del registro es confuso) | conocimiento general |

## Modelos (se descargan la primera vez; no están en el repositorio)
| Modelo | Uso | Licencia | Fuente |
| --- | --- | --- | --- |
| Kokoro-82M (`mlx-community/Kokoro-82M-bf16`) | Voz | Apache-2.0 | ficha HF |
| Whisper large-v3 (`mlx-community/whisper-large-v3-asr-fp16`) | Comprobar que la voz se entiende | Apache-2.0 | ficha HF |
| Qwen3.6 27B (vía Ollama) | Experimento de la Fase 7 | Apache-2.0 | ficha HF (`Qwen/Qwen3.6-27B`) |
| Claude Sonnet 5.5 / Haiku 5.5 | Desarrollo (Claude Code) | Servicio de Anthropic | — |

Qwen3-TTS (probado y descartado) figura como Apache-2.0 en su ficha, pero no se usa.

## Programas que se instalan aparte
| Programa | Licencia | Fuente |
| --- | --- | --- |
| Blender 5.2 | GPL; el repositorio solo incluye un script que se ejecuta dentro de Blender, no el programa | conocimiento general |
| FFmpeg | LGPL o GPL según cómo se compile | conocimiento general |
| Google Chrome | Software propietario gratuito | conocimiento general |
| Ollama | MIT | conocimiento general |
| espeak-ng (incluido en `espeakng-loader`) | GPL-3.0 | conocimiento general |

## Tipografías
Montserrat e IBM Plex Mono se cargan desde Google Fonts al renderizar el vídeo (licencia SIL Open Font License) [conocimiento general]. No se incluyen en el repositorio.

## Contenido generado
La lámpara (`viewer/public/lampara.glb`), los renders y el vídeo son obra de este proyecto. El producto «Arco» y la marca de ejemplo «Brasa» son inventados.
