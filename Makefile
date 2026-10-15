.PHONY: help check video promo2d agua blender video-vivo hyperframes viewer blender audio studio clean

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

agua:
	node video/render.mjs webgl/agua.html out/agua.mp4

promo2d:
	node video/render.mjs video/promo.html out/promo-2d.mp4

hyperframes:
	cd hyperframes/promo && npx hyperframes check && npx hyperframes render -o ../../out/promo-hyperframes.mp4

viewer:
	cd viewer && npm test && npm run build && npm run capturas

audio studio:
	@echo "Pendiente: se implementa en su fase (ver PLAN-EJERCICIO.md)"

clean:
	rm -rf out/*
