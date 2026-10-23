# Lamp studio

Local mini-studio: from ONE file (`brief.json`) it produces a 3D lamp model, a web viewer and a 20 s promo video with voice and music, and checks the result.
The plan and the research are in `docs/` (`exercise-plan.md`, `professional-level.md`, `pro-pipeline.md`). The history of what went well and badly is in `docs/journal.md` and `docs/metrics.csv`.

## How to use it

- `make setup` (once): Python environment and Node dependencies. The project path must be short (< ~90 characters): espeak-ng fails with long paths.
- `make studio` (or `make -j4 studio`): EVERYTHING from `brief.json`; it ends with `make verify` (21 checks). `BRIEF=other.json` uses another brief.
- `make variant N=cool B=brief.cool.json`: the same in a separate `git worktree` (`../<project-folder>-cool`), without overwriting this one.
- Single pieces: `make blender | viewer | hyperframes | audio`. Help: `make help`.

## Rules

- **`brief.json` is the only source** of name, tagline, benefits, voice script, palette, music and voice. After editing it: `make generate`.
  Its keys are in English; the VALUES (product text, voice script) are Spanish on purpose: they are the language of the video and the voice.
- **GENERATED files (not edited by hand):** `hyperframes/promo/index.html`, `docs/script.json`, `viewer/src/brief.generated.js`.
  The video template is `templates/hyperframes-promo.template.html` (outside `hyperframes/promo/`: otherwise `hyperframes check` fails because of two root compositions).
- **What the brief CANNOT change:** the lamp geometry, the 5 scenes and the 20 s duration. A product other than a lamp requires new code.
- Never say "done" without LOOKING at the result (contact sheet, `ffprobe`, `make verify`). Use the `render-check` skill.
- Anything that depends on time (video, shaders) must be a function of `t`: no `Date`, `requestAnimationFrame`, `setTimeout` or `Math.random` in what gets rendered.
- Small changes; if a task touches more than 5 files, a plan first. Log non-obvious failures in `docs/journal.md` and one row per attempt in `docs/metrics.csv`.
- Writing happens only inside this folder (a hook enforces it).

## Tools

Node 22, ffmpeg, Blender 5.2.2 (`/Applications/Blender.app`), Chrome, Ollama; the project's Python in `audio/.venv` (Kokoro, Whisper large-v3). No global or paid installs without notice.

## Claude Code pieces of this project (`.claude/`)

- Skill `render-check`: how to verify an output.
- Subagents: `modeler` (Blender), `web3d` (Three.js viewer), `video` (HyperFrames), `audio` (voice, music, mix). Each one carries what was learned in its area.
- Hooks (`.claude/settings.json`): `path-guard.py` blocks writing outside the project and editing generated files; `after-edit.py` regenerates/validates after editing the brief or the template.
  They are guard rails, NOT security: they only watch the Write and Edit tools; a Bash command can bypass them.

## Structure

`brief.json` · `templates/` · `scripts/` (generator, verifier, variants, captures) · `video/` (Phase 1) · `hyperframes/promo/` (Phase 2) · `viewer/` (Phase 3) · `webgl/` (Phase 3b) · `blender/` (Phase 4) · `audio/` (Phase 5) · `experiment/` and `experiment-phase7/` (Phase 7) · `dashboard/` · `out/` (results, not versioned)
