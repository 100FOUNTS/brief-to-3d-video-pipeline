#!/usr/bin/env python3
"""PreToolUse hook (Write|Edit) of this project. With exit 2 it BLOCKS the edit and returns the reason to Claude.

Blocks:
  1. writing outside the project folder (except Claude Code's temporary scratchpad, /private/tmp/claude-* and /tmp/claude-*)
  2. hand-editing files GENERATED from brief.json (they would be lost on the next `make generate`)
"""
import json, os, pathlib, sys

GENERATED = {
    "hyperframes/promo/index.html": "generated from templates/hyperframes-promo.template.html and brief.json",
    "docs/script.json": "generated from brief.json (voice.opening, benefits[].voice, voice.closing)",
    "viewer/src/brief.generated.js": "generated from brief.json (product and palette)",
}
TEMP = ("/private/tmp/claude-", "/tmp/claude-")


def block(reason):
    print(f"BLOCKED by the path-guard hook: {reason}", file=sys.stderr)
    sys.exit(2)


data = json.load(sys.stdin)
path = (data.get("tool_input") or {}).get("file_path")
if not path:
    sys.exit(0)
project = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
target = pathlib.Path(path).expanduser().resolve()
if str(target).startswith(TEMP):
    sys.exit(0)
try:
    rel = target.relative_to(project).as_posix()
except ValueError:
    block(f"{target} is OUTSIDE the project folder ({project}). This project only writes inside its own folder.")
if rel in GENERATED:
    block(f"{rel} is a GENERATED file ({GENERATED[rel]}). Edit brief.json or the template and run `make generate`; if you edit it here it will be lost.")
sys.exit(0)
