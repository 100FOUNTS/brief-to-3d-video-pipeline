# Ejercicio: Mini-estudio creativo local con Claude Code

Plan del 15 de octubre de 2026. Está pensado para un Mac (M4 Max, 36 GB de memoria, Node 22, FFmpeg, Homebrew, Ollama 0.30 y Claude Code 2.1 ya instalados).

## Qué vas a construir

Un flujo que, a partir de un **brief** (un archivo de texto), produce estas piezas para un producto original, una **lámpara de escritorio articulada**:

1. Un modelo 3D hecho por código en Blender, con renders.
2. Un visor web interactivo en Three.js con vista explosionada (el "configurador 3D" del documento).
3. Un vídeo promocional de 20 a 30 s con voz y música, hecho con HTML (el método "el código es el medio").
4. Un script que lo encadena todo: `make studio BRIEF=brief.md`.

Es el proyecto "estudio creativo automatizado" del documento, recortado a lo que se puede hacer gratis y en local. La lámpara es un producto original, así que no tiene problemas de propiedad intelectual y las piezas te sirven de portafolio.

## Qué aprenderás (mapa contra el documento)

| Tema del documento | Dónde lo practicas |
| --- | --- |
| "El código es el medio" (HTML, JS, Three.js) | Fases 1, 2 y 3 |
| WebGL2 y shaders a mano (película de mosaico de vidrio, Minecraft de Wachnik) | Fase 3b |
| Claude Dashboards (beta) | Fase 7b, opcional y según tu plan |
| Claude Motion (beta) | No incluido: no está en Pro ni en Max. Su equivalente abierto es la Fase 2 |
| Vídeo por código: `seek(t)`, Chrome sin interfaz, FFmpeg | Fase 1 |
| HyperFrames y su plugin para Claude Code | Fase 2 |
| 3D por código con Blender y Python (bpy), render y autocorrección | Fase 4 |
| "El modelo maneja el programa" (MCP) con Blender | Fase 4b |
| Python (scripts de Blender, síntesis de audio, voz, datos) | Fases 4, 5 y 7b |
| Música y voz sintetizadas, mezcla con FFmpeg | Fase 5 |
| Orquestar varios agentes, skills, hooks | Fase 6 |
| Verificar el trabajo del modelo, costes, claves del documento | Todas, con un registro de costes y fallos |
| Modelos de pesos abiertos y cuánto se parecen a Opus 5.5 | Fase 0 y Fase 7 |

**Lo que este ejercicio no cubre**, porque el programa no es abierto: Final Cut Pro, Unreal Engine, Ableton Live, Xcode, Claude Motion (cerrado y solo para Team y Enterprise) y el uso autónomo del ordenador de Astra (Codex). Los sustituyo por Blender, HyperFrames, síntesis por código y verificación con navegador. En "Extensiones" tienes cómo retomarlos más adelante.

## Reglas del ejercicio

- **Claude Code es el entorno de trabajo; el modelo es local.** Usas Claude Code conectado a Ollama con un modelo de pesos abiertos. Coste de modelo: 0 USD.
- **Opus 5.5 solo como comparación.** En la Fase 7 repites un paso difícil con Opus 5.5 y mides la diferencia. Si no quieres gastar, sáltatela.
- **Cada fase termina con algo que se puede comprobar:** un archivo, un fotograma, una prueba que pasa. Es la clave nº 1 del documento ("resultado verificable").
- **Prompts con números:** resolución, duración, paleta, restricciones. Es la clave nº 4.
- **Lleva un diario** en `docs/diario.md`: qué pediste, qué salió mal, cuánto tardó. Es lo que más aprendizaje te va a dar.
- **Registra métricas desde el primer día** en `docs/metricas.csv` (fecha, fase, modelo, minutos, intentos, resultado). Es la materia prima del dashboard de la Fase 7b.

## Estructura de carpetas

```
estudio-lampara/
  CLAUDE.md                 # reglas del proyecto para Claude Code
  brief.md                  # el brief de la lámpara
  Makefile                  # make video | make viewer | make blender | make studio
  video/
    scene.html              # Fase 1
    render.mjs
  hyperframes/              # Fase 2
  viewer/                   # Fase 3 (Vite + Three.js)
  webgl/                    # Fase 3b (WebGL2 puro)
  dashboard/                # Fase 7b
  blender/
    build_lamp.py           # Fase 4
    render.py
  audio/
    music.py                # Fase 5
    narration.py
  out/                      # resultados (no se versiona)
  docs/diario.md
  .claude/
    skills/                 # Fase 6
    agents/                 # Fase 6
    settings.json           # hooks de la Fase 6
```

## Fase 0. Preparar el entorno (1 sesión, 1-2 h)

**Objetivo:** Claude Code funcionando contra un modelo local, y saber hasta dónde llega.

**Instalar lo que falta**

```bash
brew install uv                 # si falta
brew install --cask blender     # si falta; la actual es la 5.2.2 LTS
ollama pull qwen3.6:27b         # unos 18-19 GB
ollama pull gemma4:26b          # alternativa, 16-19 GB
```

**Conectar Claude Code con Ollama**

```bash
mkdir -p ~/Documents/ejercicios/estudio-lampara && cd $_ && git init
ollama launch claude            # elige qwen3.6:27b (o usa ./scripts/claude-local.sh, ya con 64K)
# En Claude Code: /status para confirmar que habla con localhost:11434
```

Si prefieres la configuración manual: `ANTHROPIC_BASE_URL=http://localhost:11434`, `ANTHROPIC_AUTH_TOKEN=ollama`, `ANTHROPIC_API_KEY=""` y `claude --model qwen3.6:27b`. El contexto debe ser de al menos 64.000 tokens; si el modelo "se olvida" a mitad de tarea, empieza por ahí.

**Prueba de humo.** Pídele algo pequeño y comprobable: "Crea un script de Node que lea `brief.md` y cuente palabras, con una prueba." Anota cuántos segundos tarda y si usa bien las herramientas (leer, editar, ejecutar).

**Escribe `CLAUDE.md`** (Claude Code lo lee al iniciar). Plantilla:

```markdown
# Estudio lámpara
Producto original: lámpara de escritorio articulada. Prohibido copiar marcas o personajes.
## Reglas
- Todo se ejecuta con `make`. No dejes pasos manuales.
- Después de generar una imagen, un vídeo o un modelo, MÍRALO (extrae fotogramas con ffmpeg) antes de decir que está listo.
- Resolución de vídeo 1920x1080, 30 fps. Paleta en `brief.md`.
- Cambios pequeños. Si una tarea necesita más de 5 archivos, primero escribe un plan y espera.
- Registra en docs/diario.md cada fallo no obvio.
```

**Criterio de éxito:** la prueba de humo pasa y tienes anotados los tiempos del modelo local.

**Qué esperar:** un modelo local es más lento y se equivoca más que Opus 5.5. Para compensar, pide tareas pequeñas con prueba incluida y usa el modo de plan (Shift+Tab) en tareas de varios archivos.

## Fase 1. Vídeo por código con script propio (1-2 sesiones)

**Objetivo:** entender el método que hay detrás de la mayoría de vídeos de Opus 5.5: una página que dibuja el fotograma del segundo `t`.

**Instalar:** `npm init -y && npm install playwright-core` (usa tu Google Chrome, ya instalado).

**Prompt:**

> Crea `video/scene.html` de 1920x1080 que defina `window.DURATION = 8` y una función `seek(t)` que dibuje el fotograma del segundo t. Escena: fondo `#0f1115`, el texto "Lámpara Arco" aparece con fundido entre 0,5 s y 1,5 s, y una línea de acento `#ffb703` se dibuja de izquierda a derecha entre 1 s y 3 s. Todo debe depender solo de t: nada de `Date`, `requestAnimationFrame`, `setTimeout` ni CSS animations. Después crea `video/render.mjs` que abra la página en Chrome sin interfaz, llame a `seek(t)` para cada fotograma a 30 fps, capture JPEG y los pase a ffmpeg para sacar `out/titulo.mp4`. Al terminar, extrae los fotogramas de 0 s, 1 s y 4 s, míralos y confirma que no hay texto cortado.

**Criterio de éxito:** `out/titulo.mp4` de 8 s; dos renders seguidos dan fotogramas idénticos (compáralos con `ffmpeg ... -f framemd5`).

**Qué aprendes:** por qué la determinación del tiempo importa, el coste de PNG frente a JPEG (el documento midió 26 s frente a 11,5 s para 12 s de vídeo), y el bucle "renderizar, mirar, corregir".

**Reto extra:** que `seek(t)` use Canvas 2D para una gráfica animada de datos.

## Fase 2. HyperFrames (1 sesión)

**Objetivo:** hacer lo mismo con una herramienta abierta que ya trae vista previa y render, y compararla con tu script.

```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
npx hyperframes init hyperframes/promo
```

**Prompt:** "Con el plugin de HyperFrames, haz un vídeo de 20 s del producto: título, tres frases de beneficios (ligera, articulada, luz cálida), cierre con el nombre. Paleta del brief. Usa GSAP para el movimiento. Ejecuta `lint`, `check` y `snapshot` y corrige lo que falle antes de renderizar."

**Criterio de éxito:** `npx hyperframes render` produce el MP4 y `check` no da avisos.

**Qué aprendes:** la estructura `data-composition-id`, `data-start`, `data-duration`, `class="clip"`; las líneas de tiempo en `window.__timelines`; cuándo conviene una herramienta hecha frente a tu script. Escribe en el diario una tabla comparando líneas de código, tiempo de render y control.

## Fase 3. Visor 3D con Three.js (2 sesiones)

**Objetivo:** el "configurador 3D" con vista explosionada.

**Sesión A, geometría procedural.** Prompt:

> En `viewer/` crea un proyecto con Vite y Three.js. Construye la lámpara con primitivas: base cilíndrica, dos brazos (cajas largas), dos articulaciones (esferas), pantalla (cono truncado abierto) y bombilla (esfera emisiva). Cada pieza es un `Group` con nombre. Añade OrbitControls, una luz direccional con sombras suaves y un fondo neutro. Añade una prueba con Vitest que verifique que existen las 7 piezas con sus nombres.

**Sesión B, vista explosionada e interacción.** Un deslizador (0 a 1) que separa las piezas a lo largo de su eje con interpolación suave; clic en una pieza muestra su nombre y material; botón para cambiar el color de la pantalla. Pide después que use `playwright-core` para abrir la página, mover el deslizador a 0, 0,5 y 1, hacer capturas y revisarlas.

**Criterio de éxito:** `npm run dev` funciona, la prueba pasa y las tres capturas muestran las piezas separándose sin salir del encuadre.

**Qué aprendes:** escena, cámara, luces, materiales PBR, jerarquía de objetos, animación por interpolación, y cómo se verifica una interfaz 3D con capturas.

**Reto extra:** cargar el modelo `.glb` que exportas en la Fase 4 en lugar de las primitivas (`GLTFLoader`).

## Fase 3b. WebGL2 puro y shaders (1-2 sesiones)

**Objetivo:** ver lo que Three.js hace por debajo. Es la técnica de la película de mosaico de vidrio de Chris Riley ("WebGL2 y JavaScript puro, sin librerías") y de los shaders del Minecraft de Wachnik.

**Sesión A, el pipeline mínimo.** Prompt:

> Crea `webgl/agua.html`, un único archivo sin librerías, con un canvas de 1280x720 y contexto `webgl2`. Dibuja un triángulo que cubra toda la pantalla con un vertex shader y un fragment shader en GLSL ES 3.00. Pasa `u_time` y `u_resolution` como uniforms. Primer objetivo: un degradado vertical de `#0b132b` a `#1c2541` que cambie de color con `u_time`. Comprueba errores de compilación con `getShaderInfoLog` y `getProgramInfoLog` y muéstralos en consola.

**Sesión B, agua con luz.** Prompt:

> Amplía el fragment shader para simular una superficie de agua vista desde arriba: normales calculadas con 3 capas de ruido o senos a distintas frecuencias, reflejo del cielo con efecto Fresnel, brillo especular de un sol bajo y un ciclo día-noche de 20 s. Después añade una función global `seek(t)` que dibuje el fotograma del segundo t sin usar relojes (reutiliza el método de la Fase 1) y renderiza `out/agua.mp4` de 10 s con tu `render.mjs`.

**Criterio de éxito:** sin errores en la consola, tres capturas (t = 0, 5 y 10 s) claramente distintas y `out/agua.mp4` generado. Si las capturas salen negras en Chrome sin interfaz, es lo primero que hay que investigar: suele ser la configuración de GPU de Chromium.

**Qué aprendes:** vertex y fragment shaders, uniforms, ruido procedural, Fresnel, por qué un shader es una función pura del tiempo (conecta con `seek(t)`), y cómo depurar una GPU sin depurador: muchas capturas y pruebas pequeñas.

**Reto extra:** reescribe el mismo efecto como `ShaderMaterial` de Three.js y compara cuánto código te ahorra. Después úsalo como fondo animado del visor de la lámpara.

## Fase 4. Blender por código (2-3 sesiones)

**Objetivo:** la mitad "3D" del documento, en el modo headless del caso del mecha.

**Sesión A, construir y renderizar.** Prompt:

> Escribe `blender/build_lamp.py` para Blender (bpy) que construya la misma lámpara con modificadores (bisel, subdivisión), materiales de metal negro mate y pantalla de latón, un suelo, tres luces (principal, de relleno y de contorno) y una cámara. Debe ejecutarse con `blender -b -P blender/build_lamp.py -- --out out/blend`. Crea `blender/render.py` que renderice 5 fotogramas de una vuelta de cámara (turntable) en 1280x720 con Eevee. Mira los renders y corrige proporciones y reflejos hasta que se vean bien.

**Sesión B, exportar y animar.** Pide la exportación a `out/lampara.glb`, una animación de 5 s en la que la lámpara se despliega (rotación de articulaciones) y un renderizado final en vídeo corto. Mide el tiempo de render en tu M4 Max.

**Fase 4b, Blender en vivo con MCP (opcional pero recomendada)**

```bash
uvx mcp-for-blender install-addon
claude mcp add blender uvx mcp-for-blender
export DISABLE_TELEMETRY=true BLENDER_MCP_SAFE_MODE=1
```

Abre Blender, pestaña "MCP for Blender" (tecla N) y pulsa Start. Pide: "Mira la escena, ajusta la iluminación para que la pantalla brille con calidez y vuelve a mirar." **Guarda el archivo antes**; la herramienta ejecuta Python arbitrario y su socket no tiene autenticación, así que deja la conexión solo en tu máquina.

**Criterio de éxito:** `blender -b ...` regenera la lámpara y 5 renders desde cero; el `.glb` carga en el visor de la Fase 3.

**Qué aprendes:** `bpy`, escenas reproducibles por script frente a escenas hechas en vivo, el bucle "renderizar, mirar, corregir" aplicado al 3D, y por qué el MCP resulta útil pero arriesgado.

## Fase 5. Voz y música (1-2 sesiones)

**Objetivo:** la pista sonora del vídeo, sin programas de pago.

**Voz.** Kokoro-82M corre bien en Apple Silicon con MLX (Apache 2.0). Prompt: "Instala `mlx-audio` con uv y crea `audio/narration.py` que lea `docs/guion.txt` y genere `out/voz.wav` con Kokoro. Pruébalo con dos voces y deja la que suene mejor." (Piper es una alternativa más simple pero con licencia GPL.)

**Música.** Prompt:

> Crea `audio/music.py` con numpy que sintetice 24 s de música ambiental a 48 kHz: acordes de pad en Do mayor 7 a 70 bpm, un arpegio suave en la octava alta, un bombo muy discreto cada compás y reverberación sencilla. Guarda `out/musica.wav`. Después con ffmpeg mézclala con `out/voz.wav` bajándola 14 dB durante la voz y normaliza a -16 LUFS. No puedes escuchar el resultado, así que genera el espectrograma con ffmpeg (`showspectrumpic`), míralo y confirma que no hay recortes (clipping) ni silencios.

**Criterio de éxito:** `out/mezcla.wav` de 24 s, sin clipping y con el volumen medido.

**Qué aprendes:** síntesis básica, sincronía de audio con vídeo, y cómo verificar audio cuando el modelo no lo puede oír (espectrogramas y medidas). Esta es la versión abierta de "Ableton por MCP"; la calidad será más sencilla, pero el aprendizaje es el mismo.

**Reto extra:** probar Strudel o Tone.js para hacer la música en el navegador.

## Fase 6. Orquestar todo (2 sesiones)

**Objetivo:** que un solo comando haga el trabajo y practicar las funciones avanzadas de Claude Code.

1. **Skills.** Crea `.claude/skills/render-check/SKILL.md` con las instrucciones de verificación (extraer 3 fotogramas, mirarlos, comprobar duración, resolución y audio con `ffprobe`) y úsala tras cada render.
2. **Subagentes.** Define en `.claude/agents/` un agente por disciplina: `modelador` (Blender), `web3d` (Three.js), `video` (HyperFrames) y `audio`. Cada uno con sus herramientas y su carpeta. Pide que se ejecuten en paralelo para las piezas independientes (es lo que el documento llama "orquestación de varios agentes").
3. **Hooks.** En `.claude/settings.json` añade un hook que, tras cada edición en `video/` o `hyperframes/`, ejecute `npx hyperframes lint`, y otro que impida escribir fuera de la carpeta del proyecto.
4. **Makefile.** `make studio BRIEF=brief.md` ejecuta Blender, exporta el `.glb`, construye el visor, renderiza el vídeo, genera el audio y los mezcla con `ffmpeg` en `out/lampara-promo.mp4`.
5. **Worktrees.** Prueba a lanzar dos variantes del vídeo (paleta cálida y paleta fría) en dos worktrees de git y compara.

**Criterio de éxito:** desde una carpeta limpia, `make studio` produce `out/lampara-promo.mp4` (20-30 s con voz y música), `out/lampara.glb` y el visor en `viewer/dist/`. Haz un segundo brief (otra lámpara, otro color) y comprueba que funciona sin tocar código.

## Fase 7. Evaluar y escalar (1 sesión)

1. **Comparar modelos.** Elige el paso que más te costó (probablemente `build_lamp.py` o el vídeo) y repítelo con otro modelo: `gemma4:31b` en local, y si quieres gastar, Opus 5.5 con esfuerzo `high`. Apunta tiempo, número de iteraciones, resultado y coste. Orden de magnitud del documento: 1-2 USD por un vídeo corto, 13-15 USD por un render complejo en Blender.
2. **Retrospectiva** en `docs/diario.md`: qué tareas fueron fiables en local, cuáles no, qué prompts funcionaron, qué automatizarías.
3. **Publicar.** Sube el visor a un hosting estático gratuito y el vídeo a donde prefieras. Revisa antes que no haya marcas ni material con derechos.

## Fase 7b. Dashboards y Motion (opcional, 1 sesión)

**Estado de estas dos funciones, comprobado el 15 de octubre de 2026 en las páginas de Anthropic:**

| Función | Free | Pro | Max | Team / Enterprise |
| --- | --- | --- | --- | --- |
| Claude Dashboards (beta) | No | **Sí** | **Sí** | Sí (en Enterprise lo activa un administrador) |
| Claude Motion (beta) | No | **No** | **No** | Sí |

La tabla de la página de precios (claude.com/pricing) y la página de ayuda de Dashboards lo confirman. Varios blogs dicen que Dashboards es solo para Team y Enterprise; están equivocados. No encontré ningún anuncio de Anthropic para llevar Motion a Pro o Max, y la propia beta avisa de que no todo lo que se prueba se mantiene.

**Con plan Pro:** Dashboards sí está disponible y Motion no. Haz la Opción A y, como la B no depende de ninguna cuenta, hazla también para comparar: eso te enseña qué te da cada una.

**Opción A, Dashboards (si tu plan es Pro o superior).** Dashboards escribe una consulta SQL por gráfico, y según la página de ayuda hay que **conectar antes los datos**: un almacén de datos (Redshift, BigQuery, ClickHouse, Databricks, Snowflake) o una aplicación conectada a Claude, como Salesforce. La página no dice si un CSV subido o Google Drive, Notion o Supabase sirven de fuente, así que no lo prometo: abre un chat, elige «Output» y «Dashboards» y comprueba qué fuentes te ofrece. Si hay una que puedas usar, pídele un dashboard con los datos de `docs/metricas.csv` (minutos, intentos y resultado por fase y por modelo). Gasta de tu límite de uso.

**Opción B, versión local y abierta (vale para cualquier plan).** Haz lo mismo con Claude Code y tu modelo local:

> Crea `dashboard/` con un script de Python que cargue `docs/metricas.csv` en SQLite y genere `dashboard/index.html` con Chart.js (cargado desde un archivo local, sin CDN). Cuatro gráficos, cada uno con su propia consulta SQL visible bajo el gráfico: minutos por fase, intentos por modelo, tasa de éxito por modelo y tendencia semanal. Verifica con una captura de `playwright-core` que los cuatro gráficos se ven.

**Motion.** No lo uses en el ejercicio salvo que tengas Team o Enterprise. Su idea (animación escrita como código, donde puedes editar cualquier palabra o número y exportar MP4) es la misma que practicas con tu script de la Fase 1 y con HyperFrames en la Fase 2. Si tienes acceso, pídele el vídeo de la lámpara y compáralo con el de HyperFrames en tiempo, control y calidad.

**Criterio de éxito:** un dashboard (A o B) que muestre tus propias métricas y una nota en el diario sobre qué datos acepta Dashboards realmente.

**Qué aprendes:** consultas SQL por gráfico, cómo se conectan datos a un dashboard, y la diferencia entre una función cerrada en beta (puede cambiar de plan o desaparecer) y una cadena abierta que controlas.

## Calendario orientativo

| Semana | Fases | Entregable |
| --- | --- | --- |
| 1 | 0 y 1 | Entorno listo y `titulo.mp4` |
| 2 | 2, 3 y 3b | Vídeo con HyperFrames, visor con vista explosionada y `agua.mp4` en WebGL2 |
| 3 | 4 y 4b | Lámpara en Blender, renders y `.glb` |
| 4 | 5 y 6 | Voz, música y `make studio` |
| 5 | 7 y 7b | Comparativa de modelos, dashboard de métricas y retrospectiva |

Son unas 18-30 horas en total, a tu ritmo.

## Riesgos y cómo manejarlos

- **El modelo local falla en tareas largas.** Divide en pasos de menos de 5 archivos, exige pruebas y usa el modo de plan. Si algo no sale tras 3 intentos, anótalo y prueba con otro modelo en vez de insistir.
- **Contexto corto.** Si Claude Code "olvida" instrucciones, sube el contexto de Ollama a 64K o más y mantén `CLAUDE.md` corto.
- **Memoria.** Con 36 GB, un modelo de 24 GB más Blender o Chrome puede apretar. Cierra aplicaciones durante los renders o usa `gemma4:26b`.
- **El MCP de Blender ejecuta código arbitrario.** Guarda antes, usa el modo seguro y solo en localhost.
- **Licencias.** Revisa las de Qwen3.6 y Gemma 4 antes de vender algo hecho con ellas (no las pude confirmar). Kokoro es Apache 2.0, Piper es GPL.
- **Honestidad con los resultados.** Como avisa el documento, las demos de internet son las que salieron bien. Guarda también tus fallos.

## Extensiones cuando lo termines

- **Manim** (Python, versión estable 0.20.1 según su documentación) para un vídeo explicativo de cómo funciona el flujo.
- **Gaussian splatting** para reconstruir un objeto real desde un vídeo de móvil y verlo en la web.
- **Agente de QA** que abra el visor con `playwright-core` y pruebe flujos como un usuario (el equivalente abierto del caso de Claire Vo).
- **Segundo producto** (un reloj con vista explosionada, un configurador de zapatillas) para convertir el flujo en servicio: "configurador 3D más vídeo" es una de las ideas de negocio del documento.
- **Si más adelante quieres Astra y Codex:** repite la Fase 4 con Computer Use sobre Blender y compara con el método por script.
