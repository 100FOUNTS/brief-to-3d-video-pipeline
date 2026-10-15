# Cómo se hace esto a nivel profesional y en la frontera, y qué cuesta

Investigado el 15 de octubre de 2026. **Cómo leerlo:** cada dato lleva su fuente. Casi todas son blogs y comparativas (marcado **[S]**), que se contradicen en precios; las páginas oficiales o artículos de revista son **[P]**. Lo que sale de mi razonamiento y no de una fuente lo marco **[mío]**. Los precios cambian cada mes: son orientativos, no presupuestos.

## Resumen
1. **Lo que hicimos es un flujo real y vigente**, no un juguete: vídeo y 3D «como código» (HyperFrames/Remotion, Three.js, Blender por Python) es exactamente lo que usan los equipos que automatizan producción.
2. **La frontera pasa por tres sitios**: vídeo generado por IA (Veo, Kling, Runway, Seedance), 3D generado por IA (Rodin, Tripo, Meshy) y agentes que orquestan herramientas (ComfyUI, Claude Code, USD).
3. **A nivel profesional el dinero no está en las herramientas** (casi todo cuesta céntimos por pieza) **sino en la licencia y la revisión humana**. Esto último **no lo he podido cuantificar**: no encontré tarifas fiables de estudios o freelancers, y no las invento.
4. **Lo que más separa nuestro ejercicio de un estudio** no es la tecnología sino el control de calidad, los derechos (voz, música, modelos) y la entrega con estándares.

---

## 1. Vídeo y gráficos en movimiento

### Vídeo por código (lo que hicimos)
| Opción | Qué es | Coste |
| --- | --- | --- |
| **HyperFrames** (la que usamos) | HTML + GSAP → MP4, Apache 2.0, plugin para Claude Code | 0 USD, sin pago por render. Fuente: [repositorio](https://github.com/heygen-com/hyperframes) **[P]** |
| **Remotion** | Vídeo desde componentes React | Gratis para particulares y organizaciones de hasta 3 personas. Creators 25 USD por asiento al mes; **Automators 0,01 USD por render con mínimo de 100 USD al mes**; Enterprise desde 500 USD al mes. Fuente: [precios](https://www.remotion.dev/docs/license/pricing) **[P/S]** |
| **Remotion Lambda** | Render distribuido en tu AWS | Ejemplos de su documentación: un vídeo de 1 minuto en HD ≈ 0,017–0,021 USD y uno de 10 minutos ≈ 0,10 USD (de una versión antigua; volver a medir). [Docs](https://www.remotion.dev/docs/lambda/cost-example) **[P]** |
| **Shotstack** | API de vídeo con plantillas JSON | Desde ≈ 39 USD al mes (200 créditos a 0,20 USD el minuto renderizado) o 0,30 USD el minuto sin suscripción. [Comparativa](https://www.wireflow.ai/blog/creatomate-vs-shotstack) **[S]** |
| **Creatomate** | API de vídeo con plantillas | Desde ≈ 41–54 USD al mes (2.000 créditos); el coste por minuto a 1080p va de 0,10 a 0,84 USD según la fuente. [Comparativa](https://www.plainlyvideos.com/blog/best-video-editing-api) **[S]** |

**Cómo lo hace un equipo profesional [mío, conocimiento general, no verificado hoy]:** plantillas de After Effects o Remotion alimentadas por datos, render en granja, control de versiones de los guiones y revisión humana antes de entregar.

### Vídeo generado por IA (frontera)
Cuesta por segundo de vídeo y sirve para **personas y tomas realistas**, justo lo que nuestro método no puede hacer (tu documento original lo avisaba).
| Modelo | Precio aproximado por segundo | Nota |
| --- | --- | --- |
| Veo (Google) | 0,05 – 0,60 USD (típico 0,40 con audio) | Cada pasada llega a 8 s |
| Kling 3.0 | 0,07 – 0,126 USD | El «económico» |
| Runway Gen-4.5 | 0,12 USD (12 créditos a 0,01) | Sin extras de reescalado |
| Seedance 2.0 | 0,07 (480p) – 0,37 USD (1080p) | Facturación por tokens en 2.5 |
| Sora | 0,10 – 0,75 USD según la fuente | **Estado incierto**: una fuente dice que se cierra el 24 de sep de 2026 y otra que la web y app cerraron el 26 de abril; comprobar con OpenAI |

Fuentes **[S]**: [fluxnote](https://fluxnote.io/guides/ai-video-model-pricing-comparison-2026), [Crazyrouter](https://crazyrouter.com/en/blog/ai-video-generation-api-pricing-may-2026-comparison), [AI Video Cost Calculator](https://aivideotoolbox.com/cost-calculator). Los precios de cada proveedor difieren según resolución, audio y si pasas por un agregador.

### Cómo se orquesta a nivel de estudio
- **ComfyUI** (grafos de nodos) aparece como la columna vertebral para control fino: encadenar relleno, mapas de profundidad y reiluminación hasta fotogramas limpios para composición. Fuente: [blog de Comfy](https://blog.comfy.org/p/the-8-best-ai-creative-workflow-platforms) **[S, del propio fabricante]**.
- **Ubisoft** describe un pipeline con agentes sobre sus microservicios USD (n8n + ComfyUI) que convierte briefs en listas de activos y previsualizaciones. Es el ejemplo más sólido que encontré: un [artículo de ACM](https://dl.acm.org/doi/10.1145/3819990.3820033) **[P]**.
- **Utopai Studios** produce un largometraje animado que combina animación tradicional y vídeo generativo ([Wikipedia](https://en.wikipedia.org/wiki/Text-to-video_model), **[S]**).
- Un documento afirma que DNEG usa nodos propios de ComfyUI dentro de Nuke: es una fuente secundaria sin verificar, no lo tomes como cierto.

---

## 2. 3D en la web y configuradores de producto

### Tecnología
- **Three.js** es lo que usamos (r186). Hoy el renderizador recomendado en las guías es **WebGPURenderer** (desde r171, con alternativa automática a WebGL2). WebGPU alcanzó «Baseline» en enero de 2026 en Chrome/Edge 113+, Safari 26+ y Firefox 141+ en Windows; Firefox en Mac con Apple Silicon y Linux/Android van por detrás. Soporte global ≈ 87 % (caniuse, agosto de 2026) según una fuente y ≈ 70 % según otra. Fuentes **[S]**: [vr.org](https://vr.org/articles/webgpu-baseline-2026-three-js-webxr-default), [utsubo](https://www.utsubo.com/blog/frontier-web-apis-2026-production-ready). **Esto responde la duda que dejé abierta: sí, WebGPU ya se usa en producción** (Three.js, Babylon.js, Figma, según las fuentes).
- **Nota para tu código:** la guía de migración avisa de que en r186 se eliminó `PCFSoftShadowMap` para WebGPURenderer, justo el aviso que nos salió en la Fase 3.

### Optimizar un modelo 3D para la web (lo que NO hicimos)
Nuestro `.glb` pesa 250 KB porque no lleva texturas. Un producto real sí, y el flujo profesional es:
- **`gltf-transform optimize`**: reducir texturas primero (suelen ser el 80 % o más del archivo), cuantizar vértices, comprimir geometría, simplificar y limpiar duplicados.
- **Meshopt o Draco, nunca los dos a la vez.** Meshopt es la opción habitual con animaciones; Draco comprime algo más pero decodifica más lento.
- **KTX2** para ahorrar memoria de la GPU en móviles.
- Referencias orientativas de una sola fuente: un modelo de producto típico baja de 8–15 MB a 1–2 MB; menos de 800 KB para escenas «hero». Guarda siempre el original sin optimizar (es una pérdida). Fuente **[S]**: [guía de optimización de GLB](https://svilenkovic.com/3d/glb-optimization).
- Para AR (USDZ de Apple, `model-viewer`) no encontré información fiable: hay que ir a la documentación de cada uno.

### Plataformas de configuración comerciales
| Plataforma | Coste según las fuentes | Nota |
| --- | --- | --- |
| **Threekit** (empresas) | Por cotización: desde 999 USD/mes (antiguo) hasta 30.000–100.000+ USD al año | Implantación de 3 a 6 meses. [Capterra](https://www.capterra.com/p/181527/3D-Product-Configurator/), [cpq3d](https://cpq3d.com/3d-product-configurator-cost/) **[S]** |
| **Vectary** | Pro 25–29 USD por usuario al mes; Business 79 | Es herramienta de diseño y visor, **no** un configurador con precios. **[S]** |
| **Zakeke** | Alternativa accesible para pymes | **[S]**, sin cifras fiables |
| **CPQ3D** | 3–12 € por solicitud de presupuesto tras 10 gratis | **[S]** |
| **Three.js / Babylon.js / PlayCanvas** | Código abierto; el coste es alojamiento y tiempo de desarrollo | No encontré cifras: lo anoto como vacío |

**Dónde encaja nuestro visor [mío]:** es la base de lo que ofrecen estas plataformas (modelo, piezas, color, vista explosionada), pero **sin** lo que realmente pagan los clientes grandes: lógica de precios y variantes, pedidos, integración con ERP y catálogo.

### Generar el 3D con IA (frontera)
| Servicio | Coste por modelo (aprox.) | Licencia/nota |
| --- | --- | --- |
| Tripo | 0,05 – 0,20 USD; plan Pro 19,90 USD al mes por 3.000 créditos | La capa gratuita es **no comercial** |
| Meshy | 0,10 – 0,30 USD | La gratuita sale con CC BY 4.0: se puede vender pero hay que citarlos |
| Rodin (Hyper3D) | 0,40 – 0,80 USD (créditos a 1,50 USD) | Una fuente exige suscripción de empresa (120 USD al mes) para la API; otra lo contradice |

Fuentes **[S]**: [3D AI Studio](https://www.3daistudio.com/3d-generator-ai-comparison-alternatives-guide/how-much-does-ai-3d-model-generation-cost), [comparativa en DEV](https://dev.to/trify3dhq/best-ai-3d-model-generator-tripo-vs-meshy-vs-rodin-2026-34cl). La primera es de un competidor que vende su propio agregador. **Este es justo el método que el servidor MCP de Blender trae integrado** (`generate_3d` con Tripo, Hunyuan3D y Hyper3D Rodin).

---

## 3. Blender y render

| Servicio de render en la nube | Precio por hora de GPU |
| --- | --- |
| Sky Render Farm | ≈ 0,65 USD (RTX 5090, por segundos) |
| RenderJuice | 1,27 – 1,73 USD (planes desde 49 USD al mes) |
| Blender.farm | ≈ 3 USD (2,25 en el paquete mayor) |
| RenderStreet | 4,49 USD por hora de servidor (L40S) |
| iRender | 8,20 – 9 USD (servidores dedicados) |

Fuentes **[S]**: [Blender.farm](https://www.blender.farm/pricing), [RenderJuice](https://www.renderjuice.com/pricing), [Sky Render Farm](https://www.skyrenderfarm.com/blog/render-farm-pricing-in-2026-how-much-does-cloud-rendering-cost), [RenderStreet](https://render.st/plans-pricing/). Cada una factura en unidades distintas y una comparativa dice que una granja cobraba un 42 % más que otra por la misma hora de RTX 5090: **prueba siempre con tu propia escena**.

**Nuestro caso [mío, aritmética con esas tarifas]:** la animación de 120 fotogramas tardó 61,5 s en tu Mac (≈ 0,017 horas de GPU). En una granja a 3 USD la hora serían ≈ 0,05 USD; entre 0,01 y 0,15 USD según la granja. Para este tamaño de trabajo, **el render no es un coste relevante**.

**Lo que hace un estudio y nosotros no [mío, conocimiento general, no verificado hoy]:** Cycles en lugar de Eevee para calidad final, gestión de color (ACES/OCIO), escenas en **USD** entre programas (Houdini/Solaris, Maya, Omniverse), seguimiento de activos y revisión por planos. No encontré fuentes fiables sobre Omniverse ni sobre Firefly en pipelines de estudio.

---

## 4. Voz y música

### Voz
- **ElevenLabs** (referencia comercial): según una fuente del 12 de octubre de 2026, **0,08 USD por 1.000 caracteres** con Eleven v4 y **0,04** con v4 Turbo; guías anteriores daban 0,10 y 0,05. La capa gratuita **no permite uso comercial**; el plan Starter es el más barato con licencia comercial; Business cuesta 990 USD al mes. Fuentes **[S]**: [puter](https://developer.puter.com/tutorials/elevenlabs-api-pricing/), [cekura](https://www.cekura.ai/blogs/elevenlabs-pricing), [precios oficiales](https://elevenlabs.io/pricing/api) **[P]** (que no pude cargar).
- **Nuestro caso [mío]:** el guion tiene 206 caracteres, así que sería **≈ 0,008–0,017 USD**.
- **Calidad percibida:** en la arena de [Artificial Analysis](https://artificialanalysis.ai/text-to-speech/leaderboard) **[P]**, Eleven v4 Turbo es primero (Elo 1328, propietario), seguido de varios modelos propietarios de Qwen y Gemini. El mejor de pesos abiertos es Fish Audio Drama 3 (1242), pero **pesa 24 GB y su licencia es de investigación**; Kokoro, el que usamos, es el 56.º (Elo 1061). A oído, para este guion en español, **te gustó más Kokoro que Qwen3-TTS**.

### Música
- **Generada con IA (Suno, Udio):** el panorama de derechos está **a medias**. Udio y Suno cerraron acuerdos con Universal (solo Udio) y Warner (ambos) entre octubre y noviembre de 2025; Universal y Sony con Suno siguen sin resolver según el [Financial Times](https://www.musicbusinessworldwide.com/sunos-licensing-talks-with-major-labels-in-limbo-with-no-path-forward-report/) **[P]**. En Suno, Pro (10 USD al mes) y Premier (30 USD) incluyen derechos comerciales de canciones nuevas, pero una sola fuente dice que desde el 3 de septiembre de 2026 el uso comercial depende de una descarga permitida: **sin verificar**. Udio es un «jardín cerrado»: lo creado apenas sale de la plataforma. Fuentes **[S]**: [Undetectr](https://undetectr.com/blog/suno-commercial-use), [genre-ai](https://genre-ai.app/blog/suno-vs-udio-licensing-deals-2026).
- **ElevenLabs Music:** se factura en créditos (900 por minuto, según una fuente **[S]**).
- **Lo que hicimos [mío]:** música sintetizada por código, sin samples ni modelos: no hay ningún problema de derechos, a costa de sonar sencilla.

---

## 5. Orquestarlo con agentes de IA

| Concepto | Dato |
| --- | --- |
| Planes de Claude | Pro 20 USD (17 anual) · Max 5x 100 USD · Max 20x 200 USD · Team: Standard ≈ 25 USD/asiento (20 anual), Premium ≈ 125 (100 anual), mínimo 5 miembros · Enterprise a medida. Fuente **[S]**: [superblocks](https://www.superblocks.com/blog/claude-code-pricing); lo del plan Pro lo confirma la [página de precios de Anthropic](https://claude.com/pricing) **[P]**. Si Team Standard incluye Claude Code completo **es una discrepancia entre fuentes** |
| Precio por millón de tokens (entrada / salida) | Opus 5.5 4 / 20 USD [P, Anthropic] · Sonnet 5.5 2 / 10 [S] · Haiku 5.5 0,10 / 0,50 [S] · GPT-6.1 Sol 2 / 10 [P, OpenAI] · GPT-6 Astra 10 / 50 (sin confirmar) |
| Rendimiento en tareas de código (frontera) | Opus 5.5: 66,4 % en Terminal-Bench 4.0 frente al 57,9 % de Astra, según [Anthropic](https://www.anthropic.com/claude-opus-5-5) **[P]**, que advierte de que a este nivel los márgenes engañan |
| Coste por tarea (un solo dato) | Benchmark de Rails: Opus 5.5 acertó el 65,3 % a 10,53 USD por tarea; GPT-6.1 Sol el 60,8 % a 0,80 **[S, publicación en X]** |
| Casos «de frontera» | De tu documento original (fuentes secundarias): migración de HAProxy de C a Rust en 9,5 h, 40 PR encadenados en Stripe, auditoría de 200.000 líneas en menos de 3 h |
| Nuestro experimento | El modelo local hizo la tarea bien pero ~7 veces más lento que Sonnet; **un solo intento por modelo**, no es estadística |

**Cómo lo hacen los equipos [mío, con la excepción de Ubisoft arriba]:** orquestan con una herramienta de flujos (n8n, ComfyUI o código), versionan todo, miden con evaluadores automáticos y dejan a una persona la aprobación. Es la misma forma que montamos en pequeño.

---

## 6. Cuánto costaría hacer ESTE promo con servicios de pago [mío, ilustrativo]
Aritmética sobre las tarifas de arriba. **No es un presupuesto**: no incluye el trabajo humano, que es el coste real y del que no tengo cifras.

| Pieza | Lo que hicimos | Con servicios de pago (orden de magnitud) |
| --- | --- | --- |
| Vídeo de 20 s | HyperFrames, gratis | Remotion Lambda ≈ 0,007 USD; Shotstack 0,07–0,10 USD |
| Vídeo generado por IA (si se quisiera una toma realista de 20 s) | No aplica | 1,00–12,00 USD **por intento** (0,05–0,60 USD/s); con 10 intentos, 10–120 USD |
| 3D | Blender por código, gratis | Un modelo generado por IA: 0,05–0,80 USD |
| Render | 61,5 s en tu Mac | 0,01–0,15 USD en granja |
| Voz | Kokoro, gratis | 0,008–0,017 USD |
| Música | Código, gratis | Suno Pro 10 USD/mes, o licencia de librería |
| Modelo de IA | Plan Pro (20 USD/mes) | Opus 5.5 por API: depende de los tokens |
| **Total de herramientas** | **0 USD fuera del plan Pro** | **Menos de ≈ 30 USD al mes para este volumen**, salvo que se use vídeo generado |

---

## 7. Qué le falta a nuestro ejercicio para ser «pro» [mío, análisis]
1. **Entrega con estándares:** perfiles de códec y color acordados con el cliente, y el nivel de sonido que exija cada destino (nosotros usamos −16 LUFS, razonable para web; no lo comprobé contra ninguna especificación de plataforma).
2. **Derechos y trazabilidad:** de dónde sale cada voz, música y modelo, con sus licencias (Kokoro Apache 2.0 sí; Whisper y Qwen no los verifiqué).
3. **Optimización del `.glb`** (texturas, compresión) y pruebas en móviles reales.
4. **Pruebas visuales de regresión** automáticas y revisión humana de cada entrega (nosotros miramos hojas de contactos a mano).
5. **Accesibilidad y rendimiento medidos** del visor (lo cuidé, pero no con una auditoría).
6. **Varias repeticiones del experimento de modelos**, tareas más grandes y un modelo más: la comparación que hicimos tiene un intento por modelo.
7. **Lo humano:** dirección de arte, guion y criterio. Las herramientas lo abaratan, no lo sustituyen.

## Fuentes principales
[Anthropic · Opus 5.5](https://www.anthropic.com/claude-opus-5-5) · [Precios de Claude](https://claude.com/pricing) · [Artificial Analysis · TTS](https://artificialanalysis.ai/text-to-speech/leaderboard) · [Remotion · precios](https://www.remotion.dev/docs/license/pricing) · [HyperFrames](https://github.com/heygen-com/hyperframes) · [ACM · Ubisoft](https://dl.acm.org/doi/10.1145/3819990.3820033) · [Music Business Worldwide](https://www.musicbusinessworldwide.com/sunos-licensing-talks-with-major-labels-in-limbo-with-no-path-forward-report/) · [Blender.farm](https://www.blender.farm/pricing) · [RenderJuice](https://www.renderjuice.com/pricing) · [Sky Render Farm](https://www.skyrenderfarm.com/blog/render-farm-pricing-in-2026-how-much-does-cloud-rendering-cost) · [vr.org · WebGPU](https://vr.org/articles/webgpu-baseline-2026-three-js-webxr-default) · [fluxnote · vídeo IA](https://fluxnote.io/guides/ai-video-model-pricing-comparison-2026) · [3D AI Studio](https://www.3daistudio.com/3d-generator-ai-comparison-alternatives-guide/how-much-does-ai-3d-model-generation-cost) · [Comfy](https://blog.comfy.org/p/the-8-best-ai-creative-workflow-platforms)
