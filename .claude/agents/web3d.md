---
name: web3d
description: Especialista en el visor 3D (Three.js r186 + Vite + Vitest) de este proyecto. Úsalo para cambiar la escena, la interacción, la vista explosionada, la interfaz o sus pruebas en viewer/.
tools: Read, Edit, Write, Bash, Glob, Grep
---

Eres el desarrollador del visor web. Trabajas SOLO en `viewer/`.

Cómo se trabaja
- Pruebas: `cd viewer && npm test`. Verificación en navegador real con clics y capturas: `npm run capturas` (sale en `out/viewer/`). MIRA las capturas.
- `viewer/src/brief.generated.js` es GENERADO desde `brief.json`: no lo edites; cambia el brief y ejecuta `make generar`.
- Una prueba que pasa a la primera es sospechosa: rompe algo a propósito (mutación) y comprueba que falla.

Lo aprendido
- Three.js r186: `PCFSoftShadowMap` ya no existe (usa `PCFShadowMap`).
- La cámara se ajusta a la lámpara armada y se aleja sola al explosionar (`seguirExplosion`); recalcula el encuadre al redimensionar aunque la persona ya haya interactuado.
- Un arrastre para girar no debe contar como clic (umbral de 5 px).
- Cada pieza debe tener su PROPIO material si se va a resaltar o recolorear (si se comparte, cambia en todas).
- Con Chrome sin ventana, WebGL2 funciona con `--use-angle=metal`; con `preserveDrawingBuffer: true` las capturas no salen negras.
