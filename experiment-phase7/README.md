# Phase 7 experiment: recorded runs

This folder is the **historical record** of the controlled experiment described in `docs/journal.md` and `docs/retrospective.md`.
Each subfolder is one participant (a model, a reference solution, two deliberately broken "mutants" and an empty folder), evaluated by `experiment/phase7/evaluate.py`.

**Kept verbatim in Spanish on purpose:** `prompt.md`, `CLAUDE.md` and the generated `video/scene.html` / `video/render.mjs` are exactly what the models received and produced. Translating them would falsify the record (the task asks for the Spanish text "Lámpara Arco").
Only the evaluator's output (`evaluation.json`) and the scripts that run the experiment (`experiment/phase7/`) were translated.

The session logs (`session.json`, `errors.txt`) are not published: they carry session identifiers and account notices. The measured results are in `experiment/phase7/results.json`.
