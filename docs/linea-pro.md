# La línea del proyecto a nivel profesional (v2): herramienta concreta por etapa

La v1 usaba palabras genéricas («editor humano», «compositor», «alojamiento y analítica», «varios formatos»). Esta versión nombra, en cada etapa, **el producto o modelo concreto que lidera hoy (15 de octubre de 2026)**, las alternativas, **cómo se automatiza** y qué hicimos nosotros.

**Hecha** = completa para este tamaño · **Parcial** · **Faltó**.
**[P]** fuente oficial o ranking medido (Artificial Analysis, Adobe, ACM) · **[S]** blog o comparativa (se contradicen entre sí) · **[mío]** conocimiento general mío, no verificado hoy · **no investigado** = no lo busqué y no invento la cifra.

**Aviso de método:** «líder hoy» significa *primero en un ranking medido* o *el más citado*, no «lo que usan todos los estudios». No encontré datos fiables de qué usa cada estudio; lo que sí hay son rankings y precios publicados.

```
PREPARAR            3D + WEB                                   VÍDEO Y SONIDO                    CERRAR
1 Brief ─ 2 Guion ─ 3 Arte ─► 4 Modelado ─ 5 Materiales ─ 6 Optimizar ─ 7 Visor ─ 17 Publicar ─ 18 Analítica
                              └► 8 Render ─► 9 Vídeo ─ 10 Voz ─ 11 Música ─ 12 Mezcla ─ 13 Montaje
                                              14 Formatos y subtítulos ─ 15 Revisión y QC ─ 16 Derechos y procedencia
19 ORQUESTACIÓN (recorre todo)
```

## Tabla resumen

| # | Etapa | Líder hoy (herramienta / IA) | Cómo se automatiza | Lo que usamos | Estado |
| --- | --- | --- | --- | --- | --- |
| 1 | Brief | **Claude Opus 5.5** (1.º en el índice de inteligencia de Artificial Analysis, 58; Sonnet 5.5 va 56) [P] | API de Claude / Claude Code → `brief.json` | `brief.json` escrito por Sonnet 5.5; sin cliente | Parcial |
| 2 | Guion y storyboard | Claude Opus 5.5 para el guion; **LTX Studio, Boords, Katalist** para el storyboard [S] | Guion por API; storyboard generado a partir del guion [S] | Guion de 41 palabras, sin storyboard | Parcial |
| 3 | Dirección de arte | **GPT Image 2.5 Sunburst** (1.º en imagen, 1217) [P]; **Figma Make, Google Stitch, Midjourney, Recraft** [S] | Skill `/figma` de HyperFrames importa activos, tokens y componentes de Figma [P: skill instalada] | Paleta de 10 colores + 2 fuentes en el brief | Hecha (básica) |
| 4 | Modelado 3D | **Blender 5.2** (a partir de CAD) o 3D generado: **Tripo, Meshy, Rodin** [S] | Scripts `bpy`; servidor **Blender MCP** | Blender por script y por MCP (7 piezas) | Hecha (básica) |
| 5 | Materiales y texturas | **Adobe Substance 3D** (Painter 12, Sampler con Firefly: texto→textura e imagen→material) [P: Adobe] | Poco: las funciones generativas son de la aplicación y gastan créditos Firefly | Colores planos PBR | Parcial |
| 6 | Optimizar 3D para web | **gltf-transform** (CLI), meshopt o Draco, KTX2 [S] | Línea de comandos, encaja en CI | Nada (250 KB sin texturas) | Faltó |
| 7 | Visor web | **Three.js** (el nuestro), Babylon.js, PlayCanvas; plataforma **Threekit** [S] | Código en repositorio + despliegue | Three.js 0.186, 18 pruebas | Hecha (básica) |
| 8 | Render 3D | **Blender Cycles** + gestión de color; granjas de render [S] | `blender -b` por línea de comandos | Eevee local, 120 fotogramas en 61 s | Hecha (básica) |
| 9 | Vídeo | Motor por código: **HyperFrames, Remotion, Shotstack, Creatomate**. Vídeo con IA: **Wan 3.0** (1.º, 1174, 12 USD/min), **Seedance 2.5** (1160), **MiniMax H3** (1159, pesos abiertos) [P] | CLI y APIs; HyperFrames trae 11 skills para Claude Code | HyperFrames, 20 s a 1080p30 | Hecha |
| 10 | Voz | **ElevenLabs v4 Turbo** (1.º en síntesis de voz, 1328) [P] | API REST | Kokoro-82M local, verificada con Whisper large-v3 | Hecha |
| 11 | Música | **ElevenLabs Music v2.5** (0,15 USD/min; licencias comerciales), **Suno v6** (el mejor en voces), **Google Lyria 3.5** (0,08 USD/canción por API), **Mureka V9** (instrumental), **Stable Audio 3** [S] | APIs de ElevenLabs y Google | Música sintetizada con numpy | Parcial |
| 12 | Mezcla y masterización | Voz: **Auphonic** (EBU R128, ATSC A/85). Música: **iZotope Ozone 12**, **LANDR**, **RoEx Automix** [S] | Auphonic y LANDR tienen servicio en la nube; **Ozone**: no lo comprobé | FFmpeg: sidechain + `loudnorm` −16 LUFS | Hecha (automática) |
| 13 | Montaje y color | **Adobe Premiere + Firefly**, **DaVinci Resolve**, **Descript** (edición por texto) [S] | Conector de Adobe por MCP [S]; no lo probé | `mux` automático con FFmpeg | Parcial |
| 14 | Formatos, subtítulos y doblaje | Subtítulos: skill `/embedded-captions` de HyperFrames (36 estilos, transcripción local) [P: skill]. Recortes verticales: **OpusClip, Reap** [S]. Doblaje: **ElevenLabs Dubbing v2**, **HeyGen** (con sincronía labial), **Rask AI** [S] | HyperFrames deriva la relación de aspecto del destino: 16:9, 9:16 (TikTok/Reels/Shorts), 1:1 (feed) [P: skill]; doblaje por API | Un solo MP4 de 1920×1080, sin subtítulos | Faltó |
| 15 | Revisión y control de calidad | Revisión: **Frame.io**, **Wipster**, **Ziflow** [S]. QC técnico: **Telestream Baton** (no investigado) | Frame.io se integra con Premiere y Resolve [S] | 21 comprobaciones propias + mutantes + hojas de contactos | Parcial |
| 16 | Derechos y procedencia | **C2PA Content Credentials** + marca invisible (**SynthID** de Google). Art. 50 de la Ley de IA de la UE [S] | Firmar al exportar; comprobar que la plataforma no borre los metadatos [S] | Nada de procedencia; licencias de modelos sin verificar del todo | Parcial |
| 17 | Publicación | Visor: **Cloudflare Pages, Vercel, Netlify**. Vídeo: **Cloudflare Stream, Mux, Vimeo** [S] | Despliegue por CLI desde CI [mío] | `localhost:5173` | Faltó |
| 18 | Analítica | **PostHog, Mixpanel, Amplitude, GA4, Plausible** [S] | SDK en el visor + eventos (p. ej. «cambió el color») [mío] | Nada (solo un dashboard de nuestras métricas) | Faltó |
| 19 | Orquestación | **Claude Code con Opus 5.5**, skills y servidores MCP; **n8n + ComfyUI** (ComfyUI se llama por REST con `--listen` y se consulta `/history/{id}`) [S]. Caso real: **Ubisoft**, con agentes sobre USD [P: ACM] | Todo lo anterior encadenado | `make studio`, worktrees, hooks, subagentes | Hecha (muy bien) |

## Detalle por etapa: qué hace, dónde se rompe, cuánto cuesta

**1–2. Brief y guion.** El modelo de lenguaje más potente en la medición independiente es Claude Opus 5.5 (58 puntos; Sonnet 5.5, 56) [P]. Precio de la API de Opus 5.5: 4 / 20 USD por millón de tokens (entrada / salida) [P]. Para el storyboard no medí calidad: solo encontré que LTX Studio, Boords y Katalist existen y generan storyboards desde un guion [S]. **Precios de los tres: no investigado.**

**3. Arte.** El primero en el ranking de generación de imagen es GPT Image 2.5 Sunburst [P]. Para diseño de interfaces, Figma Make y Google Stitch son los citados [S]. Lo comprobable en tu máquina: la skill `/figma` de HyperFrames, que ya está instalada, importa lo que haya en Figma (activos, tokens, componentes). **Precios: no investigado.**

**4–5. Modelado y materiales.** Blender es gratuito. La generación 3D con IA cuesta 0,05–0,80 USD por modelo [S]. Substance 3D: la función «imagen → material» **exige la suscripción Substance 3D Collection** y todo lo generativo gasta créditos de Firefly; la licencia barata de Steam (Indie) **no los incluye** [P: Adobe y Meshy]. **Precio de la Collection: no lo encontré.**

**6. Optimizar.** Un producto real baja de 8–15 MB a 1–2 MB con meshopt o Draco (una de las dos) y KTX2 [S]. Herramientas gratuitas; el coste es tiempo.

**7. Visor.** A medida es gratis más tiempo. Threekit: desde 999 USD/mes hasta 30.000–100.000+ USD/año; Vectary, 25–79 USD por usuario/mes (no es configurador) [S]. WebGPU ya es estándar en todos los navegadores desde enero de 2026 [P].

**8. Render.** Granja de render: 0,65–9 USD por hora de GPU [S]. Nuestra animación: ≈ 0,01–0,15 USD. **Motor en tiempo real (Unreal Engine 5.8) frente a Cycles para producto: no lo pude comparar, no investigado.**

**9. Vídeo.** Por código: Remotion Lambda ≈ 0,02 USD/min; Shotstack 0,20–0,30 USD/min [S]. Con IA, el primero (Wan 3.0) cuesta 12 USD por minuto generado [P]; un clip de 20 s ≈ 4 USD por intento. MiniMax H3 tiene **pesos abiertos**, así que en teoría se podría correr en local; **no comprobé si cabe en tu Mac**.

**10. Voz.** ElevenLabs: 0,04–0,08 USD por 1.000 caracteres [S]; nuestro guion cuesta ≈ 0,01 USD. La capa gratuita **no permite uso comercial**; Business, 990 USD/mes [S].

**11. Música.** Las fuentes se contradicen y son blogs [S]. Lo que coincide: Udio quedó limitado (descargas apagadas tras el acuerdo con discográficas), ElevenLabs es la opción con licencia comercial más recomendada, Google Lyria es la elección práctica por API. Una sola fuente afirma que Suno cambió a v6 (9 de septiembre) y que ElevenLabs lanzó Music v2.5 (11 de septiembre): trátalo como no confirmado. **No hay ranking medido de música: no conseguí la página de Artificial Analysis.**

**12. Mezcla.** Ozone 12: 249–499 USD pago único [S]. LANDR: desde ≈ 9 USD/mes (las fuentes varían) [S]. Auphonic nivela con las normas EBU R128, ATSC A/85 y la de Apple [S]; **no verifiqué sus valores exactos ni su precio**. **Adobe Podcast Enhance: sin resultados útiles.**

**13. Montaje.** Premiere con Firefly, DaVinci Resolve, Descript. **Precios: no investigado.** Nuestro montaje fue automático; sin retoque de color.

**14. Formatos, subtítulos y doblaje.** Precios por API (agosto de 2026, una sola comparativa [S]): ElevenLabs Dubbing v2 2,20 USD/min **sin** sincronía labial; HeyGen 2,00 USD/min (rápido) o 4,00 (preciso) **con** sincronía labial; Rask 0,78–2,40 USD/min. Suscripciones: ElevenLabs Starter 6 y Creator 22 USD/mes; HeyGen Creator 24–29 USD/mes; Rask lo bloquea tras el plan de 150 USD/mes (otra fuente da 60 USD) [S]. Para este proyecto, doblar los 20 s a 2 idiomas costaría ≈ 1,5 USD con ElevenLabs o ≈ 2,7 USD con HeyGen precisión [mío, cuenta sobre precios [S]].

**15. Revisión.** Frame.io: 15 USD por miembro/mes; Team, 25 USD por miembro; capa gratuita con 2 miembros y 2 GB [S]. Wipster: desde ≈ 10–12 USD/mes para una persona (otra fuente da 25 USD/mes fijos hasta 3 asientos; **no concuerdan**) [S]. **VMAF y QC de entrega automáticos (Telestream Baton): no investigado.**

**16. Derechos y procedencia.** El Art. 50 de la Ley de IA de la UE obliga a marcar de forma legible por máquina el contenido generado por IA; **no nombra C2PA**, pero el Código de Prácticas lo usa como ejemplo junto a una marca de agua invisible como SynthID [S]. Las fuentes discrepan sobre la fecha de aplicación (2 de agosto de 2026 para todo, o hasta el 2 de diciembre para sistemas ya en el mercado): **hay que mirar el texto oficial**. Multas máximas citadas: 15 millones de euros o el 3 % de la facturación [S]. Adobe Firefly y otros ya incrustan C2PA; algunas plataformas lo borran al subir [S]. **Mi proyecto actual no emite vídeo generado por IA, pero sí voz sintética: no sé si eso entra, requiere abogado.**

**17–18. Publicación y analítica.** Los nombres salen de la investigación anterior; **no anoto precios porque no los tengo contrastados hoy.**

**19. Orquestación.** Claude: Pro 20 USD/mes (17 anual), Max 100–200, Team 25–125 USD por asiento [S/P]. La lección de n8n: los agentes sin una persona que apruebe los pasos con efectos externos fallan (una fuente cuenta un agente que mandó 47 correos de más); es una anécdota de un blog, no un dato medido [S].

## Qué hicimos y qué faltó

| | Etapas |
| --- | --- |
| **Hechas** (8) | 3 Arte (básica) · 4 Modelado · 7 Visor · 8 Render · 9 Vídeo · 10 Voz · 12 Mezcla · 19 Orquestación |
| **Parciales** (7) | 1 Brief · 2 Guion · 5 Materiales · 11 Música · 13 Montaje · 15 Revisión · 16 Derechos |
| **Faltaron** (4) | 6 Optimizar 3D · 14 Formatos, subtítulos y doblaje · 17 Publicación · 18 Analítica |

## Costes juntos
| Concepto | Lo que hicimos | Con lo más potente de la lista |
| --- | --- | --- |
| Herramientas del ejercicio | **0 USD** fuera del plan Pro (20 USD/mes) | Voz 0,01 USD + música (0,08–0,15 USD) + render (≈ 0,15 USD) ≈ **< 1 USD** por pieza [mío, suma] |
| Si el vídeo fuera generado por IA | No aplica | Wan 3.0: ≈ 4 USD por intento de 20 s |
| Doblaje de los 20 s a 2 idiomas | No aplica | ElevenLabs (sin labios): 2,20 × 0,33 min × 2 ≈ **1,5 USD**. HeyGen precisión (con labios): 4,00 × 0,33 × 2 ≈ **2,7 USD** [mío, cuenta sobre precios [S]] |
| Suscripciones fijas si se quisiera todo | Plan Pro 20 USD/mes | Claude Max 100–200 + Frame.io 15–25/miembro + ElevenLabs Creator 22 + HeyGen 24–29 ≈ **160–280 USD/mes** [mío, suma de rangos [S]] |
| Personas (brief, guion, arte, edición, revisión, legal) | Tú y yo | **No investigado; no invento cifras** |

## Qué sigue sin investigar
Precios de storyboard, Premiere, Resolve, Descript, Substance Collection, alojamiento y analítica; ranking de música; Unreal Engine 5.8 frente a Cycles; QC automático de entrega (VMAF, Baton); Claude Agent SDK o Temporal en producción creativa; qué usa cada estudio de verdad.
