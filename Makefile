# Creative studio. `make studio` does everything from ONE file: brief.json (or BRIEF=other.json).
SHELL := /bin/bash
BRIEF ?= brief.json
BLENDER := /Applications/Blender.app/Contents/MacOS/Blender
PY := audio/.venv/bin/python
HF := npx --yes hyperframes@0.8.161   # pinned version (the same as hyperframes/promo/package.json)
ENGINE := $(shell python3 scripts/brief_get.py voice.engine --brief $(BRIEF) 2>/dev/null)
VOICE := $(shell python3 scripts/brief_get.py voice.name --brief $(BRIEF) 2>/dev/null)
LABEL := $(if $(filter kokoro,$(ENGINE)),$(VOICE),$(ENGINE)-$(VOICE))

.PHONY: help setup check studio generate pieces piece-blender piece-viewer piece-video piece-audio final verify \
        blender viewer hyperframes audio audio-both audio-qwen3 audio-verify video promo2d water live-video variant clean

help:
	@echo "make setup                     - creates the Python environment (audio/.venv) and installs the Node dependencies"
	@echo "make studio [BRIEF=other.json] - EVERYTHING from the brief: 3D lamp, viewer, video with voice and music, and checks"
	@echo "make -j4 studio                - same, but the 4 independent pieces in parallel"
	@echo "make verify                    - checks the final output (video, audio, glb, viewer)"
	@echo "make variant N=cool B=brief.cool.json - a variant in a separate git worktree"
	@echo "make check                     - installed tools and models"
	@echo "Single pieces: blender viewer hyperframes audio · extras: video promo2d water live-video audio-qwen3 audio-both"

check:
	@./scripts/check-env.sh

# espeak-ng (inside the Kokoro voice) stops finding its data if the path exceeds ~160 characters (measured: 159 works, 161 fails;
# the error shows up as "phontab: No such file" pointing at the machine where it was built). That is why the path is checked before creating the environment.
setup:
	@len=$$(( $${#PWD} + 70 )); \
	  if [ $$len -gt 155 ]; then echo "ERROR: the project path is too long ($$len characters up to espeak-ng-data; the limit is ~160)."; \
	  echo "Move or clone the project to a shallower folder (e.g. ~/lamp-studio) and try again."; exit 1; fi
	@command -v uv >/dev/null || { echo "uv is missing: brew install uv"; exit 1; }
	uv venv --python 3.12 audio/.venv
	uv pip install --python $(PY) -r audio/requirements.txt
	npm ci
	cd viewer && npm ci
	@echo "Done. If you do not have them yet, you also need: FFmpeg, Blender 5.2 (brew install ffmpeg; brew install --cask blender) and Google Chrome. Check with: make check"

# ---------------------------------------------------------------- the studio
studio: generate
	@mkdir -p out/logs
	@SECONDS=0; $(MAKE) --no-print-directory $(if $(findstring j,$(MAKEFLAGS)),,-j4) pieces BRIEF=$(BRIEF) && echo "== pieces ready in $$SECONDS s"
	@$(MAKE) --no-print-directory final BRIEF=$(BRIEF)
	@$(MAKE) --no-print-directory verify BRIEF=$(BRIEF)

generate:
	python3 scripts/generate_from_brief.py --brief $(BRIEF)

pieces: piece-blender piece-viewer piece-video piece-audio

# Each piece writes its log to out/logs/ (macOS make does not group the output when running in parallel) and reports if it fails.
piece-blender:
	@mkdir -p out/logs out/blender; SECONDS=0; { $(BLENDER) -b --factory-startup -P blender/build_lamp.py -- --out out/blender --frames 5 --glb out/lamp.glb --blend out/blender/lamp.blend --brief $(BRIEF) && cp out/lamp.glb viewer/public/lamp.glb; } > out/logs/blender.log 2>&1 && echo "   OK piece-blender ($$SECONDS s)" || { echo "   FAILED piece-blender:"; tail -15 out/logs/blender.log; exit 1; }

# The viewer loads the .glb exported by Blender: it is built AFTER the Blender piece (which copies it to viewer/public/).
piece-viewer: piece-blender
	@mkdir -p out/logs; SECONDS=0; ( cd viewer && npm test --silent && npm run build --silent ) > out/logs/viewer.log 2>&1 && echo "   OK piece-viewer ($$SECONDS s)" || { echo "   FAILED piece-viewer:"; tail -15 out/logs/viewer.log; exit 1; }

piece-video:
	@mkdir -p out/logs; SECONDS=0; ( cd hyperframes/promo && $(HF) check && $(HF) render -o ../../out/promo-hyperframes.mp4 ) > out/logs/video.log 2>&1 && echo "   OK piece-video ($$SECONDS s)" || { echo "   FAILED piece-video:"; tail -15 out/logs/video.log; exit 1; }

piece-audio:
	@mkdir -p out/logs; SECONDS=0; { $(PY) audio/narration.py --brief $(BRIEF) && $(PY) audio/music.py --brief $(BRIEF) && audio/mix.sh $(LABEL); } > out/logs/audio.log 2>&1 && echo "   OK piece-audio ($$SECONDS s)" || { echo "   FAILED piece-audio:"; tail -15 out/logs/audio.log; exit 1; }

final:
	audio/mux.sh $(LABEL)
	cp out/promo-hyperframes-sound-$(LABEL).mp4 out/promo-final.mp4

verify:
	$(PY) scripts/verify_output.py --brief $(BRIEF)

# ---------------------------------------------------------------- single pieces (as before)
blender:
	$(BLENDER) -b --factory-startup -P blender/build_lamp.py -- --out out/blender --frames 5 --glb out/lamp.glb --blend out/blender/lamp.blend --brief $(BRIEF)
	cp out/lamp.glb viewer/public/lamp.glb

viewer:
	cd viewer && npm test && npm run build && npm run captures

hyperframes: generate
	cd hyperframes/promo && $(HF) check && $(HF) render -o ../../out/promo-hyperframes.mp4

audio: generate
	$(PY) audio/narration.py --brief $(BRIEF)
	$(PY) audio/music.py --brief $(BRIEF)
	audio/mix.sh $(LABEL)
	audio/mux.sh $(LABEL)

# Phase 5: both Kokoro voices at once, to compare by ear
audio-both:
	$(PY) audio/narration.py
	$(PY) audio/music.py
	audio/mix.sh ef_dora
	audio/mix.sh em_alex
	audio/mux.sh ef_dora
	audio/mux.sh em_alex

audio-qwen3:
	$(PY) audio/narration.py --engine qwen3 --extra-window 0.6
	audio/mix.sh qwen3-ryan
	audio/mix.sh qwen3-aiden
	audio/mux.sh qwen3-ryan
	audio/mux.sh qwen3-aiden

audio-verify:
	$(PY) audio/verify_voice.py out/audio/mix_$(LABEL).wav
	$(PY) audio/measure_mix.py $(LABEL)

# ---------------------------------------------------------------- earlier phases
video:
	node video/render.mjs video/scene.html out/title.mp4

promo2d:
	node video/render.mjs video/promo.html out/promo-2d.mp4

water:
	node video/render.mjs webgl/water.html out/water.mp4

live-video:
	python3 scripts/make-live-video.py

# ---------------------------------------------------------------- variants in worktrees
variant:
	@test -n "$(N)" -a -n "$(B)" || { echo "usage: make variant N=cool B=brief.cool.json"; exit 2; }
	./scripts/variant.sh $(N) $(B)

clean:
	rm -rf out/*
