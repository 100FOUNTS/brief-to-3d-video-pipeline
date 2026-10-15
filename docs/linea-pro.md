# La línea del proyecto a nivel profesional: etapa por etapa

Proyecto de referencia: un vídeo promocional de un producto, con modelo 3D, visor web interactivo, voz y música.
**Hecha** = la hicimos completa para este tamaño · **Parcial** = la hicimos a medias · **Faltó** = no la hicimos.
**[P]** fuente oficial · **[S]** blog o comparativa (se contradicen) · **[mío]** conocimiento general mío, no verificado hoy · **no investigado** = no lo busqué, no invento la cifra.
Detalle y enlaces de cada dato: `docs/nivel-profesional.md`.

```
PREPARAR                 3D + WEB                          VÍDEO Y SONIDO                    CERRAR
1 Brief ─ 2 Guion ─ 3 Arte ─► 4 Modelado ─ 5 Materiales ─ 6 Optimizar ─ 7 Visor ─┐
                              │                                                   │
                              └► 8 Render 3D ─► 9 Vídeo ─ 10 Voz ─ 11 Música ─ 12 Mezcla ─ 13 Montaje
                                                                                         │
                  14 Calidad ─ 15 Derechos ─ 16 Entrega ─ 17 Publicar        ◄───────────┘
18 AUTOMATIZACIÓN Y OPERACIÓN (recorre todo)
```

## La tabla

| # | Etapa | ¿La hicimos? | Qué usamos | Qué usa lo pro | Coste de lo pro |
| --- | --- | --- | --- | --- | --- |
| 1 | **Brief y estrategia** | **Parcial** | `brief.md` y `brief.json` (producto, textos, paleta). Sin cliente ni objetivos medibles | Reuniones con el cliente, guía de marca, objetivos y público [mío] | Horas de personas; **no encontré tarifas fiables** |
| 2 | **Guion y storyboard** | **Parcial** | Guion de 41 palabras, una frase por escena. **Sin storyboard** dibujado | Guionista y storyboard o animática, aprobados antes de producir [mío] | No investigado |
| 3 | **Dirección de arte** (paleta, tipografía, estilo) | **Hecha** (básica) | Paleta de 10 colores y Montserrat + IBM Plex Mono, definidas en el brief | Diseñador/a, sistema de diseño (Figma o similar) [mío] | No investigado |
| 4 | **Modelado 3D** del producto | **Hecha** (básica) | Blender 5.2.2 por código: 7 piezas con bisel | Artista 3D a partir de planos CAD o escaneo; o **3D generado por IA** ([S]: Tripo, Meshy, Rodin) | IA: **0,05–0,80 USD por modelo**. Artista: no investigado |
| 5 | **Materiales y texturas** | **Parcial** | Materiales PBR de color plano (metal negro, latón). **Sin texturas** | Texturas PBR pintadas (p. ej. Substance 3D) [mío] | No investigado |
| 6 | **Optimizar el 3D para la web** | **Faltó** | Nuestro `.glb` pesa 250 KB porque no lleva texturas | `gltf-transform optimize`, compresión **meshopt o Draco** (no las dos), **KTX2**. Un producto real baja de 8–15 MB a 1–2 MB [S] | Herramientas gratuitas; el coste es tiempo |
| 7 | **Visor o configurador web** | **Hecha** (básica) | Three.js 0.186: girar, vista explosionada, color, clic en piezas, 18 pruebas | Three.js/Babylon.js/PlayCanvas a medida, o una **plataforma** con precios, variantes y pedidos | Código: gratis (más tiempo). **Threekit: 999 USD/mes hasta 30.000–100.000+ USD/año**; Vectary 25–79 USD/usuario/mes (no es configurador) [S] |
| 8 | **Render y animación 3D** | **Hecha** (básica) | Eevee en tu Mac: 5 imágenes y una animación de 120 fotogramas en 61 s | **Cycles** para calidad final, gestión de color (ACES), escenas en **USD**, **granjas de render** | **0,65–9 USD por hora de GPU** [S]. Nuestra animación: ≈ 0,01–0,15 USD |
| 9 | **Vídeo y gráficos en movimiento** | **Hecha** | HyperFrames (HTML + GSAP), 20 s a 1080p30 | After Effects con plantillas, o **Remotion / Shotstack / Creatomate**. Para personas y tomas realistas: **vídeo generado por IA** (Veo, Kling, Runway, Seedance) | Remotion Lambda ≈ 0,02 USD/min; Shotstack 0,20–0,30 USD/min [S]. **IA: 0,05–0,60 USD por segundo** (1–12 USD por 20 s, por intento) [S] |
| 10 | **Voz** | **Hecha** | Kokoro-82M (`em_alex`), local, verificada con Whisper large-v3 | **ElevenLabs** o actores de voz con dirección [mío] | ElevenLabs **0,04–0,08 USD por 1.000 caracteres** [S]; nuestro guion ≈ 0,01 USD. Actores: no investigado |
| 11 | **Música y sonido** | **Parcial** | Música sintetizada por código (sin derechos que pagar). **Sin efectos de sonido** | Compositor, biblioteca con licencia o **música con IA** (Suno, Udio) y diseño de sonido [mío] | Suno **10–30 USD/mes** (con derechos, pero los acuerdos con discográficas están a medias) [S]. Biblioteca/compositor: no investigado |
| 12 | **Mezcla y masterización** | **Hecha** (automática) | FFmpeg: la música baja con la voz, −16 LUFS, pico ≤ −1,5 dB, voz 12–19 LU sobre la música | Estación de audio (Pro Tools, Reaper...) y normas por plataforma [mío] | No investigado |
| 13 | **Montaje final y corrección de color** | **Parcial** | Ensamblado automático (`mux`); sin retoque humano | Editor humano en Premiere/DaVinci/Final Cut, corrección de color [mío] | No investigado |
| 14 | **Control de calidad y revisión** | **Parcial** | Muy buena en lo automático: 21 comprobaciones, evaluador validado con mutantes, hojas de contactos miradas a mano. **Sin revisión del cliente** | Rondas de revisión humana y aprobación del cliente; pruebas visuales automáticas [mío] | Horas de personas; no investigado |
| 15 | **Derechos y licencias** | **Parcial** | Voz Kokoro (Apache 2.0, comprobada), música propia, fuentes abiertas. **No verificadas**: Whisper y Qwen | Contratos y licencias de cada voz, música, modelo y fuente | ElevenLabs: la capa gratuita **no permite uso comercial**; Business 990 USD/mes [S]. Abogados: no investigado |
| 16 | **Entrega en todos los formatos** | **Parcial** | Un MP4 de 1920x1080, 30 fps, H.264. **Sin subtítulos ni versiones verticales/cuadradas** | Varias relaciones de aspecto, subtítulos, copias maestras [mío] | Sobre todo tiempo |
| 17 | **Publicación y medición** | **Faltó** | El visor solo corre en `localhost` | Alojamiento con CDN, analítica de uso [mío] | No investigado |
| 18 | **Automatización y operación** | **Hecha** (muy bien) | `make studio` desde `brief.json`, variantes en `git worktree`, verificador, hooks, subagentes, Claude Code (Sonnet 5.5) | Lo mismo con integración continua, colas de render y gestión de activos. **Ubisoft** lo hace con agentes sobre USD (n8n + ComfyUI) [P: ACM] | **Claude: Pro 20 USD/mes, Max 100–200, Team 25–125 USD por asiento** [S/P]. Opus 5.5 por API: 4 / 20 USD por millón de tokens [P] |

## Resultado
| | Etapas |
| --- | --- |
| **Hechas** (8) | 3 Arte · 4 Modelado · 7 Visor · 8 Render · 9 Vídeo · 10 Voz · 12 Mezcla · 18 Automatización |
| **Parciales** (8) | 1 Brief · 2 Guion · 5 Materiales · 11 Música · 13 Montaje · 14 Calidad · 15 Derechos · 16 Entrega |
| **Faltaron** (2) | 6 Optimizar el 3D · 17 Publicación |

**Lo que mejor salió** fue la automatización (18) y la verificación automática (14). **Lo que más falta** no es técnico: es lo **humano y legal** (brief con cliente, storyboard, revisión, derechos) y la **entrega** (formatos, publicación).

## Costes, juntos
| Concepto | Lo que hicimos | Con servicios de pago |
| --- | --- | --- |
| Herramientas para este volumen [mío, suma de las cifras de arriba] | **0 USD** fuera del plan Pro (20 USD/mes) | **Menos de ≈ 30 USD al mes**, sin vídeo generado por IA |
| Si se añade una toma realista generada por IA [mío] | No aplica | + **1–12 USD por intento** de 20 s |
| Trabajo humano (brief, guion, arte, edición, revisión, derechos) | Lo hicimos tú y yo | **No investigado: no tengo cifras fiables y no las invento.** Es, con diferencia, el coste real |
| Tiempo | ≈ 12 horas estimadas, repartidas en 8 fases | No investigado |

## Cómo se interpreta
Las herramientas cuestan **céntimos o unas decenas de dólares al mes** para este tamaño; lo caro a nivel profesional son las **personas**, los **derechos** y la **revisión**. Nuestro ejercicio demuestra que la parte técnica y repetible se puede automatizar; no sustituye las etapas 1, 2, 14 y 15 hechas bien.
