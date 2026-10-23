# Exercise: a local creative mini-studio with Claude Code

Plan dated 15 October 2026. It is designed for a Mac (M4 Max, 36 GB of memory, Node 22, FFmpeg, Homebrew, Ollama 0.30 and Claude Code 2.1 already installed).

> The "source document" mentioned below is a third-party summary of blog posts about advanced projects with frontier models. It is not included in this repository.

## What you are going to build

A workflow that, from a **brief** (a text file), produces these pieces for an original product, an **articulated desk lamp**:

1. A 3D model built with code in Blender, with renders.
2. An interactive web viewer in Three.js with an exploded view (the "3D configurator" from the source document).
3. A 20 to 30 s promo video with voice and music, made with HTML (the "code is the medium" method).
4. A script that chains everything: `make studio BRIEF=brief.md`.

It is the "automated creative studio" project from the source document, cut down to what can be done for free and locally. The lamp is an original product, so it has no intellectual-property problems and the pieces serve as a portfolio.

## What you will learn (map against the source document)

| Topic in the source document | Where you practice it |
| --- | --- |
| "Code is the medium" (HTML, JS, Three.js) | Phases 1, 2 and 3 |
| WebGL2 and hand-written shaders (the glass-mosaic film, Wachnik's Minecraft) | Phase 3b |
| Claude Dashboards (beta) | Phase 7b, optional and depending on your plan |
| Claude Motion (beta) | Not included: it is not on Pro or Max. Its open equivalent is Phase 2 |
| Video as code: `seek(t)`, headless Chrome, FFmpeg | Phase 1 |
| HyperFrames and its plugin for Claude Code | Phase 2 |
| 3D with code with Blender and Python (bpy), rendering and self-correction | Phase 4 |
| "The model drives the program" (MCP) with Blender | Phase 4b |
| Python (Blender scripts, audio synthesis, voice, data) | Phases 4, 5 and 7b |
| Synthesized music and voice, mixing with FFmpeg | Phase 5 |
| Orchestrating several agents, skills, hooks | Phase 6 |
| Verifying the model's work, costs, keys from the source document | All, with a log of costs and failures |
| Open-weight models and how close they get to Opus 5.5 | Phase 0 and Phase 7 |

**What this exercise does not cover**, because the program is not open: Final Cut Pro, Unreal Engine, Ableton Live, Xcode, Claude Motion (closed and only for Team and Enterprise) and Astra's autonomous computer use (Codex). I replace them with Blender, HyperFrames, synthesis by code and browser verification. Under "Extensions" you will find how to pick them up again later.

## Exercise rules

- **Claude Code is the work environment; the model is local.** You use Claude Code connected to Ollama with an open-weight model. Model cost: 0 USD.
- **Opus 5.5 only as a comparison.** In Phase 7 you repeat a hard step with Opus 5.5 and measure the difference. If you do not want to spend, skip it.
- **Every phase ends with something that can be checked:** a file, a frame, a test that passes. It is key no. 1 of the source document ("verifiable result").
- **Prompts with numbers:** resolution, duration, palette, constraints. It is key no. 4.
- **Keep a journal** in `docs/journal.md`: what you asked, what went wrong, how long it took. It is what will give you the most learning.
- **Log metrics from day one** in `docs/metrics.csv` (date, phase, model, minutes, attempts, result). It is the raw material for the Phase 7b dashboard.

## Folder structure

```
lamp-studio/
  CLAUDE.md                 # project rules for Claude Code
  brief.md                  # the lamp brief
  Makefile                  # make video | make viewer | make blender | make studio
  video/
    scene.html              # Phase 1
    render.mjs
  hyperframes/              # Phase 2
  viewer/                   # Phase 3 (Vite + Three.js)
  webgl/                    # Phase 3b (pure WebGL2)
  dashboard/                # Phase 7b
  blender/
    build_lamp.py           # Phase 4
    render.py
  audio/
    music.py                # Phase 5
    narration.py
  out/                      # results (not versioned)
  docs/journal.md
  .claude/
    skills/                 # Phase 6
    agents/                 # Phase 6
    settings.json           # Phase 6 hooks
```

## Phase 0. Prepare the environment (1 session, 1-2 h)

**Goal:** Claude Code working against a local model, and knowing how far it goes.

**Install what is missing**

```bash
brew install uv                 # if missing
brew install --cask blender     # if missing; the current one is 5.2.2 LTS
ollama pull qwen3.6:27b         # about 18-19 GB
ollama pull gemma4:26b          # alternative, 16-19 GB
```

**Connect Claude Code with Ollama**

```bash
mkdir -p ~/Documents/exercises/lamp-studio && cd $_ && git init
ollama launch claude            # choose qwen3.6:27b (or use ./scripts/claude-local.sh, already with 64K)
# In Claude Code: /status to confirm that it talks to localhost:11434
```

If you prefer the manual configuration: `ANTHROPIC_BASE_URL=http://localhost:11434`, `ANTHROPIC_AUTH_TOKEN=ollama`, `ANTHROPIC_API_KEY=""` and `claude --model qwen3.6:27b`. The context must be at least 64,000 tokens; if the model "forgets" midway through a task, start there.

**Smoke test.** Ask for something small and checkable: "Create a Node script that reads `brief.md` and counts words, with a test." Note how many seconds it takes and whether it uses the tools well (read, edit, run).

**Write `CLAUDE.md`** (Claude Code reads it at startup). Template:

```markdown
# Lamp studio
Original product: articulated desk lamp. Copying brands or characters is forbidden.
## Rules
- Everything runs with `make`. Leave no manual steps.
- After generating an image, a video or a model, LOOK AT IT (extract frames with ffmpeg) before saying it is ready.
- Video resolution 1920x1080, 30 fps. Palette in `brief.md`.
- Small changes. If a task needs more than 5 files, write a plan first and wait.
- Log every non-obvious failure in docs/journal.md.
```

**Success criterion:** the smoke test passes and you have noted the local model's times.

**What to expect:** a local model is slower and makes more mistakes than Opus 5.5. To compensate, ask for small tasks with a test included and use plan mode (Shift+Tab) on multi-file tasks.

## Phase 1. Video as code with your own script (1-2 sessions)

**Goal:** understand the method behind most Opus 5.5 videos: a page that draws the frame of second `t`.

**Install:** `npm init -y && npm install playwright-core` (it uses your Google Chrome, already installed).

**Prompt** (the on-screen text is Spanish, because it is the product content):

> Create `video/scene.html` of 1920x1080 that defines `window.DURATION = 8` and a function `seek(t)` that draws the frame of second t. Scene: background `#0f1115`, the text "Lámpara Arco" fades in between 0.5 s and 1.5 s, and an accent line `#ffb703` is drawn from left to right between 1 s and 3 s. Everything must depend only on t: no `Date`, `requestAnimationFrame`, `setTimeout` or CSS animations. Then create `video/render.mjs` that opens the page in headless Chrome, calls `seek(t)` for each frame at 30 fps, captures JPEG and pipes them to ffmpeg to produce `out/title.mp4`. When finished, extract the frames at 0 s, 1 s and 4 s, look at them and confirm that no text is cut off.

**Success criterion:** `out/title.mp4` of 8 s; two consecutive renders give identical frames (compare them with `ffmpeg ... -f framemd5`).

**What you learn:** why determinism in time matters, the cost of PNG versus JPEG (the source document measured 26 s versus 11.5 s for 12 s of video), and the "render, look, correct" loop.

**Extra challenge:** make `seek(t)` use Canvas 2D for an animated data chart.

## Phase 2. HyperFrames (1 session)

**Goal:** do the same with an open tool that already brings preview and render, and compare it with your script.

```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
npx hyperframes init hyperframes/promo
```

**Prompt:** "With the HyperFrames plugin, make a 20 s video of the product: title, three benefit sentences (light, articulated, warm light), closing with the name. Palette from the brief. Use GSAP for the motion. Run `lint`, `check` and `snapshot` and fix whatever fails before rendering."

**Success criterion:** `npx hyperframes render` produces the MP4 and `check` gives no warnings.

**What you learn:** the `data-composition-id`, `data-start`, `data-duration`, `class="clip"` structure; the timelines in `window.__timelines`; when a ready-made tool is better than your script. Write a table in the journal comparing lines of code, render time and control.

## Phase 3. 3D viewer with Three.js (2 sessions)

**Goal:** the "3D configurator" with an exploded view.

**Session A, procedural geometry.** Prompt:

> In `viewer/` create a project with Vite and Three.js. Build the lamp with primitives: a cylindrical base, two arms (long boxes), two joints (spheres), a shade (open truncated cone) and a bulb (emissive sphere). Each part is a named `Group`. Add OrbitControls, a directional light with soft shadows and a neutral background. Add a Vitest test that verifies the 7 parts exist with their names.

**Session B, exploded view and interaction.** A slider (0 to 1) that separates the parts along their axis with smooth interpolation; clicking a part shows its name and material; a button to change the shade color. Then ask it to use `playwright-core` to open the page, move the slider to 0, 0.5 and 1, take screenshots and review them.

**Success criterion:** `npm run dev` works, the test passes and the three screenshots show the parts separating without leaving the frame.

**What you learn:** scene, camera, lights, PBR materials, object hierarchy, animation by interpolation, and how a 3D interface is verified with screenshots.

**Extra challenge:** load the `.glb` model you export in Phase 4 instead of the primitives (`GLTFLoader`).

## Phase 3b. Pure WebGL2 and shaders (1-2 sessions)

**Goal:** see what Three.js does underneath. It is the technique of Chris Riley's glass-mosaic film ("WebGL2 and pure JavaScript, no libraries") and of the shaders in Wachnik's Minecraft.

**Session A, the minimal pipeline.** Prompt:

> Create `webgl/water.html`, a single file without libraries, with a 1280x720 canvas and a `webgl2` context. Draw a triangle that covers the whole screen with a vertex shader and a fragment shader in GLSL ES 3.00. Pass `u_time` and `u_resolution` as uniforms. First goal: a vertical gradient from `#0b132b` to `#1c2541` that changes color with `u_time`. Check compilation errors with `getShaderInfoLog` and `getProgramInfoLog` and show them in the console.

**Session B, water with light.** Prompt:

> Extend the fragment shader to simulate a water surface seen from above: normals computed with 3 layers of noise or sines at different frequencies, sky reflection with a Fresnel effect, specular highlight from a low sun and a 20 s day-night cycle. Then add a global function `seek(t)` that draws the frame of second t without using clocks (reuse the Phase 1 method) and render a 10 s `out/water.mp4` with your `render.mjs`.

**Success criterion:** no errors in the console, three clearly different screenshots (t = 0, 5 and 10 s) and `out/water.mp4` generated. If the screenshots come out black in headless Chrome, that is the first thing to investigate: it is usually Chromium's GPU configuration.

**What you learn:** vertex and fragment shaders, uniforms, procedural noise, Fresnel, why a shader is a pure function of time (it connects with `seek(t)`), and how to debug a GPU without a debugger: many screenshots and small tests.

**Extra challenge:** rewrite the same effect as a Three.js `ShaderMaterial` and compare how much code it saves you. Then use it as the animated background of the lamp viewer.

## Phase 4. Blender with code (2-3 sessions)

**Goal:** the "3D" half of the source document, in the headless mode of the mecha case.

**Session A, build and render.** Prompt:

> Write `blender/build_lamp.py` for Blender (bpy) that builds the same lamp with modifiers (bevel, subdivision), matte black metal materials and a brass shade, a floor, three lights (key, fill and rim) and a camera. It must run with `blender -b -P blender/build_lamp.py -- --out out/blend`. Create `blender/render.py` that renders 5 frames of a camera orbit (turntable) at 1280x720 with Eevee. Look at the renders and fix proportions and reflections until they look good.

**Session B, export and animate.** Ask for the export to `out/lamp.glb`, a 5 s animation in which the lamp unfolds (rotation of the joints) and a final render as a short video. Measure the render time on your M4 Max.

**Phase 4b, live Blender with MCP (optional but recommended)**

```bash
uvx mcp-for-blender install-addon
claude mcp add blender uvx mcp-for-blender
export DISABLE_TELEMETRY=true BLENDER_MCP_SAFE_MODE=1
```

Open Blender, "MCP for Blender" tab (key N) and press Start. Ask: "Look at the scene, adjust the lighting so the shade glows warmly and look again." **Save the file first**; the tool runs arbitrary Python and its socket has no authentication, so keep the connection on your machine only.

**Success criterion:** `blender -b ...` regenerates the lamp and 5 renders from scratch; the `.glb` loads in the Phase 3 viewer.

**What you learn:** `bpy`, scenes reproducible by script versus scenes made live, the "render, look, correct" loop applied to 3D, and why MCP is useful but risky.

## Phase 5. Voice and music (1-2 sessions)

**Goal:** the video's soundtrack, without paid programs.

**Voice.** Kokoro-82M runs well on Apple Silicon with MLX (Apache 2.0). Prompt: "Install `mlx-audio` with uv and create `audio/narration.py` that reads `docs/script.txt` and generates `out/voice.wav` with Kokoro. Try it with two voices and keep the one that sounds better." (Piper is a simpler alternative but with a GPL license.)

**Music.** Prompt:

> Create `audio/music.py` with numpy that synthesizes 24 s of ambient music at 48 kHz: C major 7 pad chords at 70 bpm, a soft arpeggio in the high octave, a very discreet kick every bar and simple reverb. Save `out/music.wav`. Then with ffmpeg mix it with `out/voice.wav`, lowering it 14 dB during the voice, and normalize to -16 LUFS. You cannot listen to the result, so generate the spectrogram with ffmpeg (`showspectrumpic`), look at it and confirm there is no clipping or silence.

**Success criterion:** `out/mix.wav` of 24 s, without clipping and with the loudness measured.

**What you learn:** basic synthesis, audio-video synchronization, and how to verify audio when the model cannot hear it (spectrograms and measurements). This is the open version of "Ableton via MCP"; the quality will be simpler, but the learning is the same.

**Extra challenge:** try Strudel or Tone.js to make the music in the browser.

## Phase 6. Orchestrate everything (2 sessions)

**Goal:** make a single command do the work and practice Claude Code's advanced features.

1. **Skills.** Create `.claude/skills/render-check/SKILL.md` with the verification instructions (extract 3 frames, look at them, check duration, resolution and audio with `ffprobe`) and use it after every render.
2. **Subagents.** Define in `.claude/agents/` one agent per discipline: `modeler` (Blender), `web3d` (Three.js), `video` (HyperFrames) and `audio`. Each with its tools and its folder. Ask for them to run in parallel for the independent pieces (it is what the source document calls "orchestrating several agents").
3. **Hooks.** In `.claude/settings.json` add a hook that, after every edit in `video/` or `hyperframes/`, runs `npx hyperframes lint`, and another that prevents writing outside the project folder.
4. **Makefile.** `make studio BRIEF=brief.md` runs Blender, exports the `.glb`, builds the viewer, renders the video, generates the audio and mixes them with `ffmpeg` into `out/lamp-promo.mp4`.
5. **Worktrees.** Try launching two variants of the video (warm palette and cool palette) in two git worktrees and compare.

**Success criterion:** from a clean folder, `make studio` produces `out/lamp-promo.mp4` (20-30 s with voice and music), `out/lamp.glb` and the viewer in `viewer/dist/`. Make a second brief (another lamp, another color) and check that it works without touching code.

## Phase 7. Evaluate and scale (1 session)

1. **Compare models.** Pick the step that cost you the most (probably `build_lamp.py` or the video) and repeat it with another model: `gemma4:31b` locally, and if you want to spend, Opus 5.5 with `high` effort. Note the time, number of iterations, result and cost. Order of magnitude from the source document: 1-2 USD for a short video, 13-15 USD for a complex Blender render.
2. **Retrospective** in `docs/journal.md`: which tasks were reliable locally, which were not, which prompts worked, what you would automate.
3. **Publish.** Upload the viewer to free static hosting and the video wherever you prefer. Check beforehand that there are no brands or material with rights.

## Phase 7b. Dashboards and Motion (optional, 1 session)

**Status of these two features, checked on 15 October 2026 on Anthropic's pages:**

| Feature | Free | Pro | Max | Team / Enterprise |
| --- | --- | --- | --- | --- |
| Claude Dashboards (beta) | No | **Yes** | **Yes** | Yes (on Enterprise an administrator enables it) |
| Claude Motion (beta) | No | **No** | **No** | Yes |

The pricing page table (claude.com/pricing) and the Dashboards help page confirm it. Several blogs say Dashboards is only for Team and Enterprise; they are wrong. I found no announcement from Anthropic to bring Motion to Pro or Max, and the beta itself warns that not everything that is tried is kept.

**With a Pro plan:** Dashboards is available and Motion is not. Do Option A and, since B does not depend on any account, do it as well to compare: that teaches you what each one gives you.

**Option A, Dashboards (if your plan is Pro or higher).** Dashboards writes one SQL query per chart, and according to the help page you must **connect the data first**: a data warehouse (Redshift, BigQuery, ClickHouse, Databricks, Snowflake) or an app connected to Claude, such as Salesforce. The page does not say whether an uploaded CSV or Google Drive, Notion or Supabase work as a source, so I do not promise it: open a chat, choose "Output" and "Dashboards" and check which sources it offers. If there is one you can use, ask it for a dashboard with the data from `docs/metrics.csv` (minutes, attempts and result per phase and per model). It uses up your usage limit.

**Option B, local and open version (valid for any plan).** Do the same with Claude Code and your local model:

> Create `dashboard/` with a Python script that loads `docs/metrics.csv` into SQLite and generates `dashboard/index.html` with Chart.js (loaded from a local file, no CDN). Four charts, each with its own SQL query visible under the chart: minutes per phase, attempts per model, success rate per model and weekly trend. Verify with a `playwright-core` screenshot that the four charts are visible.

**Motion.** Do not use it in the exercise unless you have Team or Enterprise. Its idea (animation written as code, where you can edit any word or number and export MP4) is the same one you practice with your Phase 1 script and with HyperFrames in Phase 2. If you have access, ask it for the lamp video and compare it with the HyperFrames one in time, control and quality.

**Success criterion:** a dashboard (A or B) that shows your own metrics and a note in the journal about which data Dashboards really accepts.

**What you learn:** SQL queries per chart, how data is connected to a dashboard, and the difference between a closed feature in beta (it can change plan or disappear) and an open chain that you control.

## Suggested schedule

| Week | Phases | Deliverable |
| --- | --- | --- |
| 1 | 0 and 1 | Environment ready and `title.mp4` |
| 2 | 2, 3 and 3b | Video with HyperFrames, viewer with an exploded view and `water.mp4` in WebGL2 |
| 3 | 4 and 4b | Lamp in Blender, renders and `.glb` |
| 4 | 5 and 6 | Voice, music and `make studio` |
| 5 | 7 and 7b | Model comparison, metrics dashboard and retrospective |

About 18-30 hours in total, at your own pace.

## Risks and how to handle them

- **The local model fails on long tasks.** Split into steps of fewer than 5 files, demand tests and use plan mode. If something does not work after 3 attempts, note it and try another model instead of insisting.
- **Short context.** If Claude Code "forgets" instructions, raise Ollama's context to 64K or more and keep `CLAUDE.md` short.
- **Memory.** With 36 GB, a 24 GB model plus Blender or Chrome can be tight. Close applications during renders or use `gemma4:26b`.
- **Blender's MCP runs arbitrary code.** Save first, use safe mode and only on localhost.
- **Licenses.** Check those of Qwen3.6 and Gemma 4 before selling anything made with them (I could not confirm them). Kokoro is Apache 2.0, Piper is GPL.
- **Honesty with the results.** As the source document warns, the demos on the internet are the ones that turned out well. Keep your failures too.

## Extensions when you finish

- **Manim** (Python, stable version 0.20.1 according to its documentation) for an explainer video of how the workflow works.
- **Gaussian splatting** to reconstruct a real object from a phone video and see it on the web.
- **QA agent** that opens the viewer with `playwright-core` and tests flows like a user (the open equivalent of Claire Vo's case).
- **Second product** (a watch with an exploded view, a sneaker configurator) to turn the workflow into a service: "3D configurator plus video" is one of the source document's business ideas.
- **If later you want Astra and Codex:** repeat Phase 4 with Computer Use on Blender and compare with the script method.
