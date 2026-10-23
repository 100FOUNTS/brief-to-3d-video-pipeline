#!/usr/bin/env bash
# Creates (or reuses) a git worktree at ../<project-folder>-<name> and runs `make studio` there with the given brief.
# Useful to produce a variant (another palette, another text) in a separate folder and at the same time, without overwriting the main work,
# and also to test the studio FROM SCRATCH (the worktree brings no generated files).
# Usage: scripts/variant.sh <name> <brief.json> [make-args...]      e.g.:  scripts/variant.sh cool brief.cool.json -j4
set -euo pipefail
[ $# -ge 2 ] || { echo "usage: scripts/variant.sh <name> <brief.json> [make-args]"; exit 2; }
N="$1"; B="$2"; shift 2
cd "$(dirname "$0")/.."
ROOT="$PWD"; DEST="$(cd .. && pwd)/$(basename "$ROOT")-$N"; BRANCH="variant-$N"
[ -f "$B" ] || { echo "$B does not exist"; exit 2; }
if ! git diff --quiet || ! git diff --cached --quiet; then echo "There are uncommitted changes: commit first (the worktree starts from the last commit)."; exit 2; fi
if [ ! -d "$DEST" ]; then git worktree add -q -b "$BRANCH" "$DEST" HEAD; fi
cd "$DEST"
# heavy, unversioned dependencies: linked to the main project's instead of reinstalled
for d in node_modules viewer/node_modules audio/.venv; do [ -e "$d" ] || ln -s "$ROOT/$d" "$d"; done
cp "$ROOT/$B" "./$(basename "$B")"           # the variant's brief may not be in the commit yet
echo "== variant '$N' in $DEST (brief: $(basename "$B"))"
make "$@" studio BRIEF="$(basename "$B")"
