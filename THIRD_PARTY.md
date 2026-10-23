# Third-party components and their licenses

This repository is MIT (see `LICENSE`). **It does not redistribute third-party models or programs**, with one exception: `dashboard/chart.umd.js` (Chart.js, MIT, with its license notice inside the file). Everything else is downloaded or installed when preparing the environment.

**Source of each item:** `registry` = license field of the official registry (npm or PyPI) consulted on 23 October 2026 · `HF card` = metadata of the model's Hugging Face card, same date · `general knowledge` = I did not verify it today; check it before any commercial use.

## JavaScript libraries
| Component | Version used | License | Source |
| --- | --- | --- | --- |
| three | 0.186.1 | MIT | registry |
| vite | 8.3.x | MIT | registry |
| vitest | 5.0.x | MIT | registry |
| playwright-core | 1.64.1 | Apache-2.0 | registry |
| chart.js (file included) | 4.5.1 | MIT | the file's own header |
| HyperFrames (CLI) | 0.8.161 | Apache-2.0 | registry |
| GSAP (loaded from jsDelivr, not included) | 3.14.2 | GSAP's "Standard 'no charge' license": **it is not an open-source license**; read it at gsap.com/standard-license before any commercial use | registry |

## Python libraries (`audio/requirements.txt`)
| Component | Version | License | Source |
| --- | --- | --- | --- |
| mlx | 0.32.4 | MIT | registry |
| mlx-audio | 0.5.9 | MIT | registry |
| misaki | 0.9.4 | Apache | registry |
| numpy | 2.5.4 | BSD-3-Clause (plus permissive components) | registry |
| scipy | 1.18.1 | BSD (the registry field is confusing) | general knowledge |

## Models (downloaded the first time; they are not in the repository)
| Model | Use | License | Source |
| --- | --- | --- | --- |
| Kokoro-82M (`mlx-community/Kokoro-82M-bf16`) | Voice | Apache-2.0 | HF card |
| Whisper large-v3 (`mlx-community/whisper-large-v3-asr-fp16`) | Checking that the voice is intelligible | Apache-2.0 | HF card |
| Qwen3.6 27B (through Ollama) | Phase 7 experiment | Apache-2.0 | HF card (`Qwen/Qwen3.6-27B`) |
| Claude Sonnet 5.5 / Haiku 5.5 | Development (Claude Code) | Anthropic service | — |

Qwen3-TTS (tried and discarded) is listed as Apache-2.0 on its card, but it is not used.

## Programs installed separately
| Program | License | Source |
| --- | --- | --- |
| Blender 5.2 | GPL; the repository only includes a script that runs inside Blender, not the program | general knowledge |
| FFmpeg | LGPL or GPL depending on how it is built | general knowledge |
| Google Chrome | Free proprietary software | general knowledge |
| Ollama | MIT | general knowledge |
| espeak-ng (included in `espeakng-loader`) | GPL-3.0 | general knowledge |

## Typefaces
Montserrat and IBM Plex Mono are loaded from Google Fonts when rendering the video (SIL Open Font License) [general knowledge]. They are not included in the repository.

## Generated content
The lamp (`viewer/public/lamp.glb`), the renders and the video are the work of this project. The product "Arco" and the sample brand "Brasa" are invented.
