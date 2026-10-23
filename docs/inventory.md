# Inventory: everything used in the exercise

Collected on 15 October 2026 from the machine itself (versions read with commands, not from memory). Where a **license** was not checked today, I say so.

## 1. Hardware
| | |
| --- | --- |
| Machine | Mac with an Apple M4 Max chip, 36 GB of unified memory |
| System | macOS 26.6.2 (Darwin 25.6.0) |
| Disk | `out/` 197 MB; Hugging Face cache 24 GB (16 GB are a coding model you already had) |

## 2. AI models
| Model | What it was used for | Where it runs | Size | License |
| --- | --- | --- | --- | --- |
| **Claude Sonnet 5.5** | Almost the whole exercise (code, design, analysis) and the dashboard in claude.ai | Cloud, Pro plan | n/a | Anthropic service |
| Claude Haiku 5.5 | Tests of hooks, skill and subagent (real Claude Code instances) | Cloud, Pro plan | n/a | Service |
| **Qwen3.6 27B** (`qwen3.6-64k` variant, 64K context) | Smoke test (Phase 0) and controlled experiment (Phase 7) | Local, Ollama | 17 GB | Not verified (Ollama's page does not state it) |
| **Kokoro-82M** (bf16, MLX) | The video's **voice** (`em_alex`) | Local, the Mac's GPU | 0.39 GB | Apache 2.0 (Hugging Face card) |
| **Whisper large-v3** (fp16, MLX) | Checking that the voice is intelligible (transcribing it back) | Local | 3.09 GB | Not listed on the card; not verified |
| Qwen3-TTS 1.7B, small Whisper | Tried and **discarded** (deleted) | Local | ≈4 GB | Qwen3-TTS: Apache 2.0 (card) |
| Not used | `gemma4:12b`, `qwen3.5:4b`, `qwen3:4b`, `granite4.2:3b`, `mxbai-embed-large` (were already installed) | | | |

Opus 5.5 and GPT-6 Astra were **not** used.

## 3. Programs and runtimes
| Program | Version | What for |
| --- | --- | --- |
| Claude Code | 2.1.300 | The work environment of the whole exercise |
| Node.js / npm | 22.23.1 / 10.9.8 | Video rendering, viewer, tests |
| Python (system / project) | 3.14.6 / 3.12.15 (`audio/.venv` environment) | Scripts, voice, music, dashboard |
| uv | 0.13.1 | Python environments and the MCP server |
| FFmpeg | 8.1.2 | Joining frames, mixing audio, measuring loudness, extracting images |
| Blender | 5.2.2 LTS | 3D model and renders, with code (`bpy`) |
| Google Chrome | 155.0.8059.79 | Headless browser for rendering and verifying |
| Ollama | 0.30.11 | Serving the local model |
| git / GNU Make | 2.55.0 / 3.81 | Version control, `git worktree`, orchestration (`make -j4`) |
| Homebrew, zsh | | Installing `uv` and Blender |

## 4. Libraries
**JavaScript**
| Library | Version | Use | License |
| --- | --- | --- | --- |
| three | 0.186.1 | 3D viewer (with OrbitControls, RoomEnvironment, RoundedBoxGeometry, GLTFLoader) | MIT (npm) |
| vite / vitest | 8.3.4 / 5.0.4 | Server and bundling / tests | not verified today |
| playwright-core | 1.64.1 | Driving headless Chrome (rendering and verification) | not verified today |
| chart.js | 4.5.1 | Dashboard charts | MIT (npm) |
| HyperFrames CLI | 0.8.161 (pinned) | Video from HTML | Apache 2.0 (repository) |
| GSAP | 3.14.2 (CDN) | Animation of the HyperFrames video | not verified today |

**Python (`audio/.venv`)**: mlx 0.32.4, mlx-audio 0.5.9 (MIT, PyPI), misaki 0.9.4 (Apache 2.0), espeakng-loader 0.2.4, phonemizer-fork 3.3.2, numpy 2.5.4, transformers 5.19.0, huggingface-hub 2.2.0, SQLite 3.53.1 (from the standard library).
**Inside Blender**: `bpy` and `bmesh`. **Add-on**: mcp-for-blender 2.1.9 (MIT, PyPI), installed but **not permanently enabled**.

## 5. Formats, standards and techniques
- **Graphics:** WebGL (through Three.js), **pure WebGL2** and GLSL ES 3.00 shaders (water with Fresnel), glTF/GLB 2.0, PBR materials (Principled BSDF), bevel and solidify modifiers, Eevee engine (Metal).
- **Video:** H.264 `yuv420p` with limited range and bt709, 1920x1080 at 30 fps; video as a function of time `seek(t)` (deterministic).
- **Audio:** WAV PCM, AAC at 48 kHz, sidechain (ducking), normalization to −16 LUFS with true peak ≤ −1.5 dB (EBU R128 with `ebur128`).
- **Engineering:** unit tests and **mutation** (breaking on purpose), verification in a real browser, fixed seeds for reproducibility, a single brief as the data source, templates, `git worktree`, parallelism with `make -j4`, SQL (queries with window functions), CSV.
- **Protocol/AI:** MCP (Model Context Protocol), tool use, nested Claude Code instances (`claude -p`), a controlled experiment with an automatic evaluator.

## 6. Services and accounts
- **claude.ai, Pro plan**: Claude models, Claude Code, and Claude Dashboards (beta, Dashboard template).
- **Hugging Face Hub** (downloads without a token), **npm**, **PyPI**, **Homebrew**, Ollama registry, **Google Fonts** (the first HyperFrames build downloaded Montserrat and IBM Plex Mono) and **jsDelivr** (loads GSAP).
- **Claude in Chrome** extension (connected by the author).
- **Not used**: no paid API, no cloud render or voice service.

## 7. Claude Code pieces of the project (`.claude/`)
- **1 skill** (`render-check`) and **4 subagents** (`modeler`, `web3d`, `video`, `audio`), with what was learned in each area.
- **2 hooks** (`path-guard.py`, `after-edit.py`). They only watch Write and Edit; a Bash command bypasses them.
- Installed by the HyperFrames tool outside the project: **11 skills** in `~/.claude/skills` (and linked into 4 other agent directories).

## 8. What was built (by phase)
| Phase | Result |
| --- | --- |
| 0 | Environment, `CLAUDE.md`, local model with 64K of context |
| 1, 1b | Video as code with `seek(t)`: title (8 s) and a lamp drawn on Canvas 2D (15 s) |
| 2 | 20 s promo with HyperFrames |
| 3, 3b | 3D viewer with Three.js (exploded view); water shader in pure WebGL2 |
| 4, 4b | Lamp in Blender by script (5 renders, animation, `.glb`) and live through MCP |
| 5, 5b | Voice (Kokoro), synthesized music, mixing and verification; Qwen3-TTS test |
| 6 | `make studio` from `brief.json`, a 21-check verifier, skill, subagents, hooks, variants in worktrees |
| 7, 7b | Local experiment against Sonnet, retrospective, local dashboard and one in claude.ai |
| Extra | Blender `.glb` loaded in the viewer with a model selector |

**Figures (at the time of writing):** 24 commits, 83 versioned files, ≈4,600 lines (Python 1,365, HTML 1,198, JS 745 + 232 of `.mjs`, Markdown 662, JSON 225, shell 130, CSS 77), 22 `make` targets.

## 9. Money spent
**Nothing beyond the claude.ai Pro plan** (20 USD per month, 17 if annual, according to [Anthropic's pricing page](https://claude.com/pricing)). Everything else is free or ran on the author's Mac. Claude's usage consumed plan quota, it was not billed separately. (Claude Code reports an "API-equivalent" cost per session, which is theoretical with Pro and meaningless for the local model.)

## 10. Changes made OUTSIDE the project folder
To be able to reproduce the environment, this is what was touched:
- Installed with Homebrew: `uv` and Blender (cask version).
- `~/.claude/skills/` and 4 other agent directories: 11 HyperFrames skills.
- `~/.hyperframes/`: HyperFrames configuration, with **telemetry enabled** (turn it off with `npx hyperframes telemetry disable`).
- `~/Library/Application Support/Blender/5.2/scripts/addons/blender_mcp.py`: the MCP add-on, **not enabled**.
- `~/.cache/huggingface/`: Kokoro and Whisper large-v3 (those of Qwen3-TTS and small Whisper were deleted).
- `~/.ollama`: the `qwen3.6:27b` model and its 64K variant.
- `experiment-phase7/`: the experiment's folders (included in this repository, without `node_modules` or `out/`).
- In the author's claude.ai account: a private chat and dashboard ("Dashboard de métricas CSV").
- Processes left open: the viewer server at `localhost:5173` (stopped with Ctrl+C).
