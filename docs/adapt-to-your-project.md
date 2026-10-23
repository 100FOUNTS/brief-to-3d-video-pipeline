# Adapt this repository to your own project

The repository is a worked example (a desk lamp), but its **pattern** is reusable. This guide says, by increasing effort, what you can change, where, and what is **hard-coded** today. It only states what is visible in the code; what I did not test is marked.

**What is generic and what is not**

| Generic (reuse as it is) | Specific to the lamp (you will replace it) |
| --- | --- |
| One validated `brief.json` → generated files (`scripts/generate_from_brief.py`) | The 3D model: `blender/build_lamp.py` |
| `make studio`: independent pieces in parallel, then a verifier | The viewer's parts and exploded view: `viewer/src/lamp.js` |
| Video as a function of time `seek(t)`, headless Chrome + FFmpeg (`video/render.mjs`) | The video scenes: `templates/hyperframes-promo.template.html` |
| Local voice + synthesized music + mix to −16 LUFS (`audio/`) | The list of parts the verifier expects: `scripts/verify_output.py` |
| Hooks that protect generated files, skill and subagents (`.claude/`) | |

## Level 1 · Change the content (no code, minutes)

Edit `brief.json` (or copy it to `brief.mine.json`):

| Field | Rule (enforced by the generator) |
| --- | --- |
| `product.name` | ≤ 7 characters (it is drawn at 280 px) |
| `product.tagline`, `benefits[].detail` | ≤ 40 characters |
| `benefits[].word` | ≤ 12 characters |
| `benefits[].voice` | ≤ 90 characters; it must fit its 3.2 s window |
| `benefits` | exactly **3** items; `id` in lowercase, digits and hyphens |
| `palette` | the 10 keys, `#rrggbb`; text on background needs contrast ≥ 4.5:1, `accent_label` ≥ 3:1 |
| `voice` | `engine: "kokoro"`, `name`: a Kokoro voice |
| `music` | `bpm` and `seed` (the music is deterministic) |
| `video.duration` | must stay `20` |

Then:

```bash
make generate                 # validates the brief and regenerates the dependent files
make studio                   # builds everything and verifies it
make variant N=mine B=brief.mine.json   # or: in a separate git worktree, without overwriting your main output
```

A bad brief is rejected in under a second with **all** its errors at once. Tested in Phase 6 (see the journal): `brief.brasa.json` is a different product (name, text, palette, tempo) produced with no code changes.

> **Language of the voice.** The narration language is **Spanish and fixed in the code**, not in the brief: `audio/narration.py` sets Kokoro's language code (`lang="e"`) and the Whisper check uses `language="es"` (also in `audio/verify_voice.py`). To narrate in another language you must change those places, pick a voice for that language, and review the text normalizer (`normalize()` keeps only `a-z`, `ñ` and digits, so it needs changing for non-Latin scripts). **I have not tested it**; treat it as a small refactor, not as a configuration option.

## Level 2 · Change the look of the video (code, an hour)

- The scenes, timings and motion are in `templates/hyperframes-promo.template.html` (HTML + GSAP). **Never edit `hyperframes/promo/index.html`**: it is generated, and a hook blocks it. Edit the template and run `make generate`.
- The 5-scene structure and the 20 s are fixed (see "Fixed numbers" below).
- Look at the result, do not trust `hyperframes check` alone: it passed once with an arc crossing the text (see `docs/journal.md`). Use the `render-check` skill.

## Level 3 · A different product (the real work, days)

This changes the geometry, so the lamp-specific code has to be rewritten. The places, in the order I recommend:

1. **The verifier first.** `scripts/verify_output.py` line `PARTS = [...]` lists the node names the `.glb` must contain. Change it to your parts: it becomes your acceptance test.
2. **The 3D model.** `blender/build_lamp.py`: the parameters (`POSE`), `build_lamp()` (geometry, pivots and **node names**), the materials in `prepare_scene()` and the unfolding animation in `animate_unfolding()`. Keep a root empty and one named empty per part: the viewer depends on those names.
3. **The viewer.** `viewer/src/lamp.js`: `PART_NAMES`, `INFO` (the text of each part), `EXPLOSION` (the direction each part moves), `createLamp()` (the primitives version) and `lampFromGLTF()` (it expects the node names above, a `shade-outer` mesh for the recolorable surface, and a `bulb` part that carries the light).
4. **The viewer tests.** `viewer/src/lamp.test.js` and `viewer/src/glb.test.js` assert the 7 parts and the lamp's geometry; rewrite them for your parts. They compare the Blender model against the primitives one, which is what caught a real bug (see the journal).
5. **The brief's limits.** `LIMITS` and the rules in `scripts/generate_from_brief.py`.
6. **Agents and docs.** `.claude/agents/*.md` and `CLAUDE.md` mention the lamp; update them so Claude Code works with the right context.

A prompt that works well with the project's subagents (adapt the product):

> Use the `modeler` subagent to replace the lamp in `blender/build_lamp.py` with a ceramic mug: three parts (`body`, `handle`, `coffee`). Keep the node-name convention and the `--glb` export. First update `PARTS` in `scripts/verify_output.py`. Render, **look at the images**, and run `make blender` until `make verify` passes the 3D checks.

**Fixed numbers (hard-coded today).** Changing any of them is a refactor, not a configuration:

| Fixed | Where |
| --- | --- |
| 7 parts | `PARTS` in `scripts/verify_output.py`; `PART_NAMES` in `viewer/src/lamp.js`; the tests |
| 3 benefits | `len(ben) != 3` in `scripts/generate_from_brief.py`; three scene blocks in the template |
| 5 scenes and their times | `script()` in `scripts/generate_from_brief.py` (start and window of each sentence); the template's timeline |
| 20 s | `video.duration` check in the generator; `--duration` in `audio/`; `scripts/verify_output.py` |

## Level 4 · Other operating systems (not tested)

Only macOS on Apple Silicon was tested. What is tied to it:

- **Voice and transcription** use MLX (`mlx-audio`), which only runs on Apple Silicon. On Linux or Windows you would replace Kokoro/Whisper with another local TTS/STT; `audio/narration.py` is the only file that talks to them.
- **Hard-coded macOS paths:** Blender in `Makefile` and `scripts/blender-live.sh`; Chrome in `video/render.mjs`, `scripts/capture.mjs` and `viewer/scripts/captures.mjs`; both in `scripts/check-env.sh`.
- Keep the project in a **short folder path** (< ~90 characters): espeak-ng, used by the voice, fails with long paths (see the journal).

## A good order to work in

1. Run the example once (`make setup && make studio`) so you know what "working" looks like.
2. Do Level 1 with your own text and palette; confirm `make verify` still passes.
3. Only then change the product (Level 3), verifier first, and look at every output before moving on.
4. Log what fails in your own `docs/journal.md`: it is what makes the next change faster.
