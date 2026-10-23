# Exercise retrospective (15 October 2026)

One day of work, 15 logged attempts, about 750 estimated minutes. What came out, what I learned and what I would change. The data is in `docs/journal.md`,
`docs/metrics.csv` and `dashboard/index.html`. The minutes are estimates; almost everything was done by Sonnet 5.5 in the cloud (the plan said the local model).

## What was built
From `brief.json`, `make studio` produces in ~25 s: a 20 s video with voice and music, a 3D lamp model (.glb), a web viewer with an exploded view,
5 Blender renders, and 21 automatic checks. It was tested with two different products (Arco, Brasa) without touching code.

## What worked
- **Verifying by looking, not only with tests.** Almost all the important failures were found by a contact sheet or a measurement, not by a test that passed.
- **Testing the verifier.** With negative cases (mutants) I detected three times that a check was not checking anything (the clock detector in the evaluator, the contrast, an ignored `cmp`).
- **Testing from scratch** (a clean `git worktree`): it found the failure that would have broken the project (`multiple_root_compositions`).
- **A single source of truth** (`brief.json`) with a generator that validates and regenerates: the second product came out without new code.
- **Documenting the failures** in the journal avoided repeating them and fed the subagents.

## Technical lessons that were not in the original document
1. The color format of an MP4 made from JPEGs comes out `yuvj420p` and looks washed out in some players; `yuv420p`/bt709 must be forced.
2. PNG versus JPEG depends on the scene: 7.3 s versus 8.2 s in a flat scene, 210 s versus 20 s in a shader.
3. Kokoro is not deterministic without a seed; with `mx.random.seed` it is reproducible up to rounding.
4. Small Whisper hallucinates text in silences (false error of 49–160%); with Whisper large-v3, 0–2.4%. Distrust the metric before distrusting the audio.
5. In Qwen3-TTS (mlx-audio) the `speed` parameter is ignored and the pace varies from 5 to 9.6 s for the same sentence; Kokoro sounds more natural in Spanish (the user's decision, by ear).
6. Deleting a model from the Hugging Face cache does not free space: the orphaned blobs must be deleted.
7. Blender 5.2: only engine `BLENDER_EEVEE`; a light inside an opaque sphere is blocked by its own shadow; AgX desaturates strong highlights.
8. Blender's MCP server has no password and safe mode only protects the MCP path.
9. Claude Code hooks only watch the tools they are told to; a Bash command bypasses them.

## Models: what to use for what (with the confidence the data gives)
Controlled experiment: same task (Phase 1), same prompt, same automatic evaluator, **a single attempt per model**.

| | Qwen3.6 27B local | Sonnet 5.5 cloud |
| --- | --- | --- |
| Prompt requirements | 14/14 | 14/14 |
| Unrequested quality | 1/2 (yuvj420p) | 2/2 |
| Time | 494 s | 72–78 s |
| Turns | 8 | 25 |
| Design | the golden line strikes through the text; it did not notice | more careful (underline, smooth curve) |

- **High confidence:** the local model solves a bounded, well-specified and verifiable task, and is ~6–7 times slower.
- **Medium confidence:** in that task Sonnet is more careful with details nobody asked for. A single attempt per model: there is no statistics.
- **Not tested:** large, multi-file tasks with the local model (Blender, the viewer, the brief generator) and Opus 5.5. I do not know whether the local one would cope; I do not claim it.
- My provisional recommendation: local model for small, well-defined tasks (when time does not matter or you do not want to spend quota); Sonnet for what crosses several files or demands visual judgment.

## My recurring mistakes (so as not to repeat them)
- Asserting something I had not checked (that Kokoro was identical between runs; a model's size figures; "no failures" with a check that did not look).
- Arbitrary thresholds taken from my own solution (in the experiment's evaluator, which failed a correct solution).
- Charts that suggest false conclusions (the "minutes per attempt by model" one, already removed).
- Launching work that consumes quota (repeating Sonnet in the experiment) without explaining it first.

## What I would do now
1. Repeat the experiment 3–5 times per model and with a larger task (e.g. the brief generator) before drawing conclusions.
2. Try Opus 5.5 and the local model on a multi-file task; measure quota and time.
3. (Done afterwards: the Blender .glb is loaded in the viewer; see the journal.) Extend `make studio` with the viewer's screenshots.
4. Make `verify` include an assisted visual review (a contact sheet that is always saved).
