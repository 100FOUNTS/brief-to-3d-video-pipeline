# Diario del ejercicio

Una entrada por sesión: qué pediste, qué salió mal, cuánto tardó, qué aprendiste.

## 2026-10-15 · Fase 0
- Inicio del ejercicio. Mac M4 Max, 36 GB.
- Prueba de humo con qwen3.6:27b local: 259 s, 1 intento, script y prueba correctos. Aviso: Claude Code no reconoce el modelo y asume ventana de 200k; con ANTHROPIC_API_KEY definido se desactivan los conectores de claude.ai (solo en esa sesión).
- Contexto: el servidor de Ollama carga qwen3.6:27b con 32768 por defecto (la mitad de lo recomendado). Creé la variante `qwen3.6-64k` (`ollama/Modelfile.qwen3.6-64k`) con num_ctx 65536. Carga en 17 GB, 100% GPU.
- Prueba de aguja en pajar con 39.578 tokens: acierta el dato escondido, pero la lectura tarda 269 s (unos 147 tokens/s). Consecuencia: cada sesión nueva de Claude Code cuesta minutos al arrancar; conviene sesiones largas y `CLAUDE.md` corto.
- Lanzador: `./scripts/claude-local.sh` (usa el modelo local sin tocar la configuración global).
- Memoria libre tras cargar el modelo: unos 2 GB. Cierra apps pesadas antes de renderizar con Blender.

## 2026-10-15 · Fase 1 (hecha con Sonnet 5.5, no con el modelo local)
- Resultado: `video/scene.html`, `video/render.mjs`, `make video` -> `out/titulo.mp4` (1920x1080, 30 fps, 240 fotogramas, 8 s).
- Fallo 1: el primer MP4 salió en `yuvj420p` (rango completo), porque las capturas JPEG entran como "JPEG range". Se arregla en el filtro de FFmpeg (`scale=in_range=full:out_range=limited,format=yuv420p`) y marcando bt709/tv. Sin esto algunos reproductores muestran colores apagados.
- Verificación visual: 0 s = solo fondo, 1 s = título a medio fundido y la línea sin empezar, 4 s = todo completo.
- Determinismo: dos renders -> mismos hashes de los 240 fotogramas La prueba no es vacía: dentro de un mismo render hay 96 hashes distintos de 240, que es lo esperable (los fotogramas de reposo antes de 0,5 s y después de 3 s son idénticos).
- Sorpresa: PNG (7.3 s) resultó MÁS rápido que JPEG (8.2 s), al revés que en el documento (26 s vs 11,5 s). La escena es casi plana y el PNG la comprime muy bien; con escenas complejas (3D, shaders) probablemente se invierta. Re-medir en la Fase 3b.

## 2026-10-15 · Fase 1b: escena con contenido (`video/promo.html`)
- Motivo: la escena de la Fase 1 (palabra + línea) probaba el método pero no enseñaba su potencial. Hice una de 15 s con la misma `seek(t)`: lámpara dibujada en Canvas 2D que se despliega con rebote, se enciende con parpadeo, cono de luz con partículas de polvo, giro de pose ("articulada"), cambio de color a dorado ("luz cálida") y textos por escenas.
- Técnicas: easing (smoothstep, outBack), hash determinista (`Math.sin`) en lugar de `Math.random` para el polvo y el parpadeo, composición `screen` para la luz, recorte (`clip`) al cono.
- Fallo: a 168 px la palabra "Articulada" medía unos 950 px y se salía por el borde derecho (x=1010 + 950 > 1920). Se vio en la hoja de contactos; a 140 px cabe.
- Render: 450 fotogramas en 8,3 s.

## 2026-10-15 · Fase 2: HyperFrames (hecha con Sonnet 5.5)
- Setup: las skills de HyperFrames ya estaban en `~/.claude/skills`; `npx hyperframes skills update general-video` instaló 11 skills y las enlazó en otros 4 directorios de agentes (efecto fuera del proyecto). No hizo falta instalar el plugin.
- Proyecto: `hyperframes/promo/` (BRIEF.md + index.html). Concepto: la luz es la narradora; un arco se dibuja y la luz viaja por él mientras aparece cada beneficio. Montserrat 900 + IBM Plex Mono.
- `check` pasó a la primera con 0 errores y 6 avisos de estructura (5 escenas en un solo archivo: HyperFrames recomienda sub-composiciones desde 3 cortes duros). Lo dejé así por alcance; queda como mejora.
- Fallo 1 (contraste): etiqueta "03 / 03" en #ffb703 sobre el brillo dorado: 2,72:1 (pide 3:1). Cambié las etiquetas a #ffc532.
- Fallo 2 (diseño, NO lo detecta `check`): el arco cruzaba las letras y la etiqueta caía sobre la línea. Solución: arco a 32% de opacidad tras dibujarse, bloque de texto 140 px más abajo, quitar la línea del suelo. Lección: `check` garantiza que funciona, no que se vea bien; hay que mirar la hoja de contactos.
- Render: 600 fotogramas, 20 s, 16,8 s (captura 8,2 s, codificación 2,4 s), GPU por hardware (Metal). 4 workers.
- Fuentes: el compilador descargó Montserrat e IBM Plex Mono de Google Fonts en el primer build y las guardó en caché, aunque la documentación dice que vienen incluidas.
- Telemetría de HyperFrames: ACTIVADA por defecto (`~/.hyperframes/config.json`). Se desactiva con `npx hyperframes telemetry disable`.

## 2026-10-15 · Fase 3: visor 3D con Three.js (hecha con Sonnet 5.5)
- Proyecto `viewer/` (Vite 8.3.4, Three.js r186, Vitest 5.0.4). Lámpara con 7 piezas con nombre, armada con primitivas (RoundedBoxGeometry, esferas, toros, cono abierto), materiales PBR + entorno RoomEnvironment, foco SpotLight dentro de la bombilla con sombras.
- Pruebas: 9 de Vitest (siete piezas y nombres, reposo/explosión exactos, monotonía, brazos que encajan con articulaciones, encuadre). Comprobé que detectan fallos con 2 mutaciones (quitar la bombilla; mover una articulación 0,5): ambas hacen fallar pruebas.
- Verificación en navegador real (`npm run capturas`, Chrome con WebGL2 sobre Metal en el M4 Max): deslizador, clics reales en 3 piezas, clic en vacío, color, y que arrastrar para girar NO cuenta como clic. Capturas en `out/viewer/`. Sin pantallas negras: la GPU en modo sin ventana funcionó con `--use-angle=metal`.
- Fallos encontrados: (1) en Three.js r186 `PCFSoftShadowMap` ya no existe (aviso en consola; ahora PCFShadowMap); favicon 404. (2) Con la cámara ajustada a la vista explosionada, la lámpara armada se veía pequeña. Solución: la cámara se ajusta a la armada y se aleja/recentra sola con el deslizador. (3) El borde del suelo parecía una colina: niebla del color del fondo. (4) En móvil la lámpara salía recortada porque no se reencuadraba tras interactuar y el panel era enorme: reencuadre siempre y lista de piezas en una fila deslizable.
- Lección: las pruebas unitarias no habrían detectado ninguno de los problemas visuales; las capturas sí. Y mirar la imagen mostró cosas que ninguna comprobación automática cubría.
- Pendiente: el visor aún no carga el .glb de Blender (reto de la Fase 4).

## 2026-10-15 · Fase 3b: WebGL2 puro (hecha con Sonnet 5.5)
- `webgl/gradiente.html` (parte A): pipeline mínimo sin librerías: triángulo a pantalla completa generado con `gl_VertexID` (sin buffers), vertex + fragment shader (GLSL ES 3.00), uniforms `u_time`/`u_resolution`, registro de errores con `getShaderInfoLog`. Comprobado que un error de compilación se muestra con línea y motivo (`'colorInexistente' : undeclared identifier`).
- `webgl/agua.html` (parte B): agua vista al ras con olas (3-4 senos + ruido fbm + deformación del dominio), normal por diferencias finitas, reflejo del cielo con Fresnel (Schlick), destellos del sol, nubes por ruido, estrellas de noche, ciclo día-noche de 20 s (amanecer a la derecha, atardecer a la izquierda), niebla de distancia, tono y gamma. Cielo y agua con la paleta del brief para la noche (#0b132b, #1c2541).
- Se renderiza con el mismo `video/render.mjs` de la Fase 1: la escena no se anima sola si la URL lleva `#render`; si no, corre en tiempo real. (Esto obligó a añadir `#render` a `render.mjs`.)
- Duración: el plan decía 10 s; hice 20 s para que se vea el ciclo completo (amanecer, mediodía, atardecer, noche).
- Iteraciones visuales (3 rondas con hoja de contactos): (1) cielo pálido, olas como bandas paralelas, amanecer = atardecer, destello recortado abajo, estrellas con el cielo claro; (2) sol + reflejo formaban una "píldora" sólida porque el reflejo copiaba el disco: ahora el reflejo no incluye el disco (parámetro `disco`); los destellos parecían espuma: acotados con `min(brillo, 1.0)`.
- Resultado: sin pantallas negras con `preserveDrawingBuffer: true` y GPU Metal.
- DATO CLAVE: 20 s de vídeo con shader tardan 20,0 s con JPEG y 210,5 s con PNG (10 veces más). En la Fase 1 (escena plana) PNG era más rápido (7,3 s contra 8,2 s). La documentación original medía 26 s contra 11,5 s. Conclusión: con escenas complejas usar JPEG; PNG solo gana en escenas casi planas.
- Los destellos del mediodía aún parecen un poco manchas blancas. Mejorable.
- Nuevo: `scripts/capturar.mjs` saca fotogramas sueltos y una hoja de contactos sin renderizar el vídeo (iterar mucho más rápido).

## 2026-10-15 · Fase 4 (forma 1: script de Python): Blender por código (hecha con Sonnet 5.5)
- `blender/build_lamp.py` (`make blender`): reconstruye la lámpara desde cero con `bpy` + `bmesh`, sin ventana: `blender -b --factory-startup -P blender/build_lamp.py -- --out ... [--glb ...] [--anim]`. Jerarquía de pivotes (pivote-1/2/3) para poder animar el despliegue; materiales Principled BSDF (metal negro, latón, bombilla emisiva), 3 luces de estudio + luz puntual en la bombilla, cámara con TRACK_TO.
- Introspección previa de la API 5.2.2: único motor `BLENDER_EEVEE` (no BLENDER_EEVEE_NEXT), `bmesh.ops.create_cone(radius1, radius2)`, glTF disponible, backend de GPU Metal.
- Eevee en segundo plano funciona con Metal a la primera. 5 renders 1280x720 en ~5 s (0,5 s c/u). Animación de 5 s a 24 fps (120 fotogramas): 61,5 s.
- Fallos: (1) la luz puntual estaba DENTRO de la esfera de la bombilla (radio 0,24, luz a 0,12) y la propia esfera le tapaba la luz: la bombilla no iluminaba el suelo; se arregló con `visible_shadow = False` en la esfera. (2) AgX (tono por defecto) desatura los brillos muy intensos: con la bombilla a 1800 W el charco salía gris, no dorado; a 750 W se ve cálido. (3) Suelo de 60x60 dejaba ver su borde: 300x300. (4) Equilibrar las luces de estudio contra la de la bombilla costó 5 rondas: mucha luz = suelo gris plano; poca = lámpara ilegible. (5) Un error mío: lancé la animación con `--sin-render`, que sale antes de renderizar.
- Reproducibilidad: dos ejecuciones dan renders idénticos píxel a píxel (PSNR infinito; los PNG difieren en metadatos). El GLB: JSON idéntico y geometría igual hasta 1e-36; no es idéntico byte a byte (8,6% de los bytes del binario, en 3 bufferViews; no identifiqué la causa).
- GLB: nodos con los nombres de las piezas (base, brazo-inferior, ..., pantalla, bombilla) y los pivotes. El reto de cargarlo en el visor queda pendiente: habrá que reparentar las piezas a la raíz para que la vista explosionada no arrastre a los hijos.

## 2026-10-15 · Fase 4b (forma 2: Blender en vivo con MCP) (hecha con una 2ª instancia de Claude Code, Sonnet 5.5)
- Configuración: `mcp-for-blender==2.1.9` (MIT, Siddharth Ahuja; verificado en PyPI). Complemento instalado con `install-addon` en `~/Library/Application Support/Blender/5.2/scripts/addons/blender_mcp.py` (6441 líneas, auditadas: se conecta solo a localhost:9876; telemetría con consentimiento; los dominios externos solo se usan con sus herramientas). NO usé `setup` (configura clientes MCP por su cuenta).
- Decisiones de seguridad: el complemento arranca el servidor solo (`blendermcp_auto_start_server` por defecto True), así que NO lo activé de forma permanente: se carga solo con `--addons blender_mcp` en la sesión que lanzo yo (`scripts/blender-vivo.sh`) y se cierra con `scripts/blender-vivo-parar.sh`. Telemetría desactivada (`DISABLE_TELEMETRY=true`) y modo seguro activado (`BLENDER_MCP_SAFE_MODE=1`, en `blender/mcp-blender.json`). Comprobado: solo escucha en 127.0.0.1:9876 y el puerto queda libre al cerrar.
- AVISO que el propio código declara: el modo seguro protege solo el camino del MCP; el socket del complemento acepta `execute_code` de cualquier proceso local, sin contraseña. Por eso el servidor solo debe estar encendido mientras se usa.
- No se registró ningún servidor MCP en la configuración de Claude Code: se usa un archivo (`blender/mcp-blender.json`) con `claude -p --mcp-config --strict-mcp-config`. Un servidor MCP añadido en mitad de una sesión no estaría disponible en ella, así que se lanza una segunda instancia que sí lo trae.
- Prueba de solo lectura: listó las 9 herramientas (get_addon_status, get_scene_info, look, execute_blender_code, search_assets, import_asset, generate_3d, record_trajectory_feedback, disable_telemetry) y describió la escena con exactitud. De paso encontró un BUG MÍO: el .blend guardado tenía la cámara en el origen (guardaba antes de colocarla) y la vista salía gris. Corregido en `build_lamp.py`.
- Tarea iterativa (42 s): 4 cambios mirando tras cada uno (luz-bombilla 750→2500, luz-contorno 250→700, luz-principal 190→90, luz-contorno 700→400). Informe honesto: el objetivo se cumplió a medias (charco cálido mayor y legible; lámpara aún oscura; gris del suelo sigue). El modo seguro bloqueó su primer intento por importar `os`: funciona. No guardó ningún .blend; la copia `vivo.blend` y `lampara.blend` no se tocaron.
- NO apliqué sus valores al script: el resultado no es claramente mejor. El flujo natural es explorar en vivo y pasar al script solo lo que funcione.
