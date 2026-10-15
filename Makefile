.PHONY: help check video hyperframes viewer blender audio studio clean

help:
	@echo "make check   - comprueba herramientas y modelo local"
	@echo "make studio  - (Fase 6) pipeline completo"
	@echo "make clean   - borra out/"

check:
	@./scripts/check-env.sh

# Se rellenan en las fases siguientes
video hyperframes viewer blender audio studio:
	@echo "Pendiente: se implementa en su fase (ver PLAN-EJERCICIO.md)"

clean:
	rm -rf out/*
