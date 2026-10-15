# Diario del ejercicio

Una entrada por sesión: qué pediste, qué salió mal, cuánto tardó, qué aprendiste.

## 2026-10-15 · Fase 0
- Inicio del ejercicio. Mac M4 Max, 36 GB.
- Prueba de humo con qwen3.6:27b local: 259 s, 1 intento, script y prueba correctos. Aviso: Claude Code no reconoce el modelo y asume ventana de 200k; con ANTHROPIC_API_KEY definido se desactivan los conectores de claude.ai (solo en esa sesión).
- Contexto: el servidor de Ollama carga qwen3.6:27b con 32768 por defecto (la mitad de lo recomendado). Creé la variante `qwen3.6-64k` (`ollama/Modelfile.qwen3.6-64k`) con num_ctx 65536. Carga en 17 GB, 100% GPU.
- Prueba de aguja en pajar con 39.578 tokens: acierta el dato escondido, pero la lectura tarda 269 s (unos 147 tokens/s). Consecuencia: cada sesión nueva de Claude Code cuesta minutos al arrancar; conviene sesiones largas y `CLAUDE.md` corto.
- Lanzador: `./scripts/claude-local.sh` (usa el modelo local sin tocar la configuración global).
- Memoria libre tras cargar el modelo: unos 2 GB. Cierra apps pesadas antes de renderizar con Blender.
