.PHONY: help check video promo2d hyperframes viewer blender audio studio clean

help:
	@echo "make check   - comprueba herramientas y modelo local"
	@echo "make studio  - (Fase 6) pipeline completo"
	@echo "make clean   - borra out/"

check:
	@./scripts/check-env.sh

video:
	node video/render.mjs video/scene.html out/titulo.mp4

# Se rellenan en las fases siguientes
promo2d:
	node video/render.mjs video/promo.html out/promo-2d.mp4

hyperframes viewer blender audio studio:
	@echo "Pendiente: se implementa en su fase (ver PLAN-EJERCICIO.md)"

clean:
	rm -rf out/*
