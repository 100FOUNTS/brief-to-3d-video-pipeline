#!/usr/bin/env python3
"""PostToolUse hook (Write|Edit) of this project. If something fails it exits with 2 and Claude sees the message.

  - If brief.json is edited: it validates it and regenerates what depends on it (scripts/generate_from_brief.py).
  - If another brief is edited (brief.cool.json...): it only VALIDATES it (does not touch the main project's files).
  - If the HyperFrames template is edited: it regenerates index.html and runs `npx hyperframes lint` on the result.
"""
import json, os, pathlib, re, subprocess, sys

data = json.load(sys.stdin)
path = (data.get("tool_input") or {}).get("file_path")
if not path:
    sys.exit(0)
project = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
try:
    rel = pathlib.Path(path).expanduser().resolve().relative_to(project).as_posix()
except ValueError:
    sys.exit(0)


def run(cmd, cwd, label):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[{label}] FAILED (code {r.returncode}):\n{(r.stdout + r.stderr).strip()[-1500:]}", file=sys.stderr)
        sys.exit(2)
    return r.stdout


if rel == "brief.json":
    out = run(["python3", "scripts/generate_from_brief.py", "--brief", rel], project, "generate from the brief")
    print(out.strip())
elif re.fullmatch(r"brief[^/]*\.json", rel):
    # variant brief: only validated; regenerating here would overwrite the main project's files with the variant's
    print(run(["python3", "scripts/generate_from_brief.py", "--brief", rel, "--validate"], project, "validate the brief").strip())
elif rel == "templates/hyperframes-promo.template.html":
    run(["python3", "scripts/generate_from_brief.py", "--brief", "brief.json"], project, "generate from the template")
    out = run(["npx", "hyperframes", "lint"], project / "hyperframes/promo", "hyperframes lint")
    print("template regenerated; " + out.strip().splitlines()[-1] if out.strip() else "template regenerated; lint printed nothing")
sys.exit(0)
