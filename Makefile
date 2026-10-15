# Estudio creativo de la lámpara. `make studio` lo hace todo a partir de UN archivo: brief.json (o BRIEF=otro.json).
SHELL := /bin/bash
BRIEF ?= brief.json
BLENDER := /Applications/Blender.app/Contents/MacOS/Blender
PY := audio/.venv/bin/python
MOTOR := $(shell python3 scripts/brief_get.py voz.motor --brief $(BRIEF) 2>/dev/null)
VOZ := $(shell python3 scripts/brief_get.py voz.nombre --brief $(BRIEF) 2>/dev/null)
ETQ := $(if $(filter kokoro,$(MOTOR)),$(VOZ),$(MOTOR)-$(VOZ))

.PHONY: help check studio generar piezas pieza-blender pieza-visor pieza-video pieza-audio final verificar \
        blender viewer hyperframes audio audio-ambas audio-qwen3 audio-verificar video promo2d agua video-vivo variante clean

help:
	@echo "make studio [BRIEF=otro.json]  - TODO desde el brief: lámpara 3D, visor, vídeo con voz y música, y comprobaciones"
	@echo "make -j4 studio                - igual, pero las 4 piezas independientes en paralelo"
	@echo "make verificar                 - comprueba la salida final (vídeo, audio, glb, visor)"
	@echo "make variante N=frio B=brief.frio.json - una variante en un worktree de git separado"
	@echo "make check                     - herramientas y modelos instalados"
	@echo "Piezas sueltas: blender viewer hyperframes audio · extras: video promo2d agua video-vivo audio-qwen3 audio-ambas"

check:
	@./scripts/check-env.sh

# ---------------------------------------------------------------- el estudio
studio: generar
	@mkdir -p out/logs
	@SECONDS=0; $(MAKE) --no-print-directory $(if $(findstring j,$(MAKEFLAGS)),,-j4) piezas BRIEF=$(BRIEF) && echo "== piezas listas en $$SECONDS s"
	@$(MAKE) --no-print-directory final BRIEF=$(BRIEF)
	@$(MAKE) --no-print-directory verificar BRIEF=$(BRIEF)

generar:
	python3 scripts/generar_desde_brief.py --brief $(BRIEF)

piezas: pieza-blender pieza-visor pieza-video pieza-audio

# Cada pieza escribe su registro en out/logs/ (el make de macOS no agrupa la salida en paralelo) y avisa si falla.
pieza-blender:
	@mkdir -p out/logs out/blender; SECONDS=0; { $(BLENDER) -b --factory-startup -P blender/build_lamp.py -- --out out/blender --frames 5 --glb out/lampara.glb --blend out/blender/lampara.blend --brief $(BRIEF); } > out/logs/blender.log 2>&1 && echo "   OK pieza-blender ($$SECONDS s)" || { echo "   FALLA pieza-blender:"; tail -15 out/logs/blender.log; exit 1; }

pieza-visor:
	@mkdir -p out/logs; SECONDS=0; ( cd viewer && npm test --silent && npm run build --silent ) > out/logs/visor.log 2>&1 && echo "   OK pieza-visor ($$SECONDS s)" || { echo "   FALLA pieza-visor:"; tail -15 out/logs/visor.log; exit 1; }

pieza-video:
	@mkdir -p out/logs; SECONDS=0; ( cd hyperframes/promo && npx hyperframes check && npx hyperframes render -o ../../out/promo-hyperframes.mp4 ) > out/logs/video.log 2>&1 && echo "   OK pieza-video ($$SECONDS s)" || { echo "   FALLA pieza-video:"; tail -15 out/logs/video.log; exit 1; }

pieza-audio:
	@mkdir -p out/logs; SECONDS=0; { $(PY) audio/narration.py --brief $(BRIEF) && $(PY) audio/music.py --brief $(BRIEF) && audio/mix.sh $(ETQ); } > out/logs/audio.log 2>&1 && echo "   OK pieza-audio ($$SECONDS s)" || { echo "   FALLA pieza-audio:"; tail -15 out/logs/audio.log; exit 1; }

final:
	audio/mux.sh $(ETQ)
	cp out/promo-hyperframes-sonido-$(ETQ).mp4 out/promo-final.mp4

verificar:
	$(PY) scripts/verificar_salida.py --brief $(BRIEF)

# ---------------------------------------------------------------- piezas sueltas (como antes)
blender:
	$(BLENDER) -b --factory-startup -P blender/build_lamp.py -- --out out/blender --frames 5 --glb out/lampara.glb --blend out/blender/lampara.blend --brief $(BRIEF)

viewer:
	cd viewer && npm test && npm run build && npm run capturas

hyperframes: generar
	cd hyperframes/promo && npx hyperframes check && npx hyperframes render -o ../../out/promo-hyperframes.mp4

audio: generar
	$(PY) audio/narration.py --brief $(BRIEF)
	$(PY) audio/music.py --brief $(BRIEF)
	audio/mix.sh $(ETQ)
	audio/mux.sh $(ETQ)

# Fase 5: las dos voces de Kokoro a la vez, para comparar a oído
audio-ambas:
	$(PY) audio/narration.py
	$(PY) audio/music.py
	audio/mix.sh ef_dora
	audio/mix.sh em_alex
	audio/mux.sh ef_dora
	audio/mux.sh em_alex

audio-qwen3:
	$(PY) audio/narration.py --motor qwen3 --extra-ventana 0.6
	audio/mix.sh qwen3-ryan
	audio/mix.sh qwen3-aiden
	audio/mux.sh qwen3-ryan
	audio/mux.sh qwen3-aiden

audio-verificar:
	$(PY) audio/verificar_voz.py out/audio/mezcla_$(ETQ).wav
	$(PY) audio/medir_mezcla.py $(ETQ)

# ---------------------------------------------------------------- fases anteriores
video:
	node video/render.mjs video/scene.html out/titulo.mp4

promo2d:
	node video/render.mjs video/promo.html out/promo-2d.mp4

agua:
	node video/render.mjs webgl/agua.html out/agua.mp4

video-vivo:
	python3 scripts/hacer-video-vivo.py

# ---------------------------------------------------------------- variantes en worktrees
variante:
	@test -n "$(N)" -a -n "$(B)" || { echo "uso: make variante N=frio B=brief.frio.json"; exit 2; }
	./scripts/variante.sh $(N) $(B)

clean:
	rm -rf out/*
