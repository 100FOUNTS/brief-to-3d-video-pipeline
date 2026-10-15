.PHONY: help check video promo2d agua blender video-vivo audio hyperframes viewer blender audio studio clean

help:
	@echo "make check   - comprueba herramientas y modelo local"
	@echo "make studio  - (Fase 6) pipeline completo"
	@echo "make clean   - borra out/"

check:
	@./scripts/check-env.sh

video:
	node video/render.mjs video/scene.html out/titulo.mp4

# Se rellenan en las fases siguientes
blender:
	/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P blender/build_lamp.py -- --out out/blender --frames 5 --glb out/lampara.glb --blend out/blender/lampara.blend

video-vivo:
	python3 scripts/hacer-video-vivo.py

audio:
	audio/.venv/bin/python audio/narration.py
	audio/.venv/bin/python audio/music.py
	audio/mix.sh ef_dora
	audio/mix.sh em_alex
	audio/mux.sh ef_dora
	audio/mux.sh em_alex

audio-verificar:
	audio/.venv/bin/python audio/verificar_voz.py out/audio/mezcla_ef_dora.wav out/audio/mezcla_em_alex.wav
	audio/.venv/bin/python audio/medir_mezcla.py ef_dora
	audio/.venv/bin/python audio/medir_mezcla.py em_alex

agua:
	node video/render.mjs webgl/agua.html out/agua.mp4

promo2d:
	node video/render.mjs video/promo.html out/promo-2d.mp4

hyperframes:
	cd hyperframes/promo && npx hyperframes check && npx hyperframes render -o ../../out/promo-hyperframes.mp4

viewer:
	cd viewer && npm test && npm run build && npm run capturas

studio:
	@echo "Pendiente: se implementa en su fase (ver PLAN-EJERCICIO.md)"

clean:
	rm -rf out/*
