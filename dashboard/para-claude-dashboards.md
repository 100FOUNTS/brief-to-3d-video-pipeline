# Opción A: Claude Dashboards (claude.ai) con las métricas del estudio

## Resultado (probado el 15 de oct de 2026, con la extensión de Claude en Chrome)
- **Se hizo.** En la cuenta del usuario (plan Pro) se creó el dashboard **«Métricas del ejercicio»** adjuntando `docs/metricas.csv` al chat de la plantilla Dashboard (Beta):
  (privado: no se pulsó «Compartir»). Chat: «Dashboard de métricas CSV».
- **Tiene** 3 indicadores (748,2 min · 47 intentos · 13 fases) y 4 gráficos (minutos por fase, intentos por fase, fases por resultado, minutos acumulados), cada uno con su «SQL equivalente».
- **Coincide con la opción B** (`dashboard/index.html`): mismas cifras.

## Lo que había supuesto mal
Escribí antes que un CSV «no se podía usar directamente» como fuente, porque la página de ayuda solo cita almacenes de datos y apps conectadas (Salesforce...).
**Era falso en la práctica:** adjuntar el CSV al chat funciona. Pero hay un matiz que Claude declaró (se lo pedí en el mensaje):
> «Este dashboard no ejecuta SQL sobre el archivo adjunto. Lee el CSV y agrega en el navegador. El SQL de cada gráfico es la consulta equivalente.» (y comprobó que da las mismas cifras en SQLite)

Es decir: es un dashboard **estático sobre el CSV subido** (no se refresca desde una fuente viva), y su «SQL» es explicativo, no el que se ejecuta.

## Diferencias que vale la pena saber
- «Fases por resultado»: Claude cuenta **fases distintas** (12 ok, 1 parcial); `dashboard/index.html` cuenta **filas** (cada intento registrado), por eso sus cifras difieren.
- Los minutos son estimaciones (el dashboard lo avisa); con 15 filas no es estadística.
- Para **actualizarlo** hay que volver a adjuntar el CSV nuevo en el chat (no se refresca solo).
- Gasta cuota de uso del plan (una respuesta de unos 2-3 minutos con Sonnet 5.5).

## Cómo repetirlo
1. claude.ai → Artefactos → **+** → **Dashboard (Beta)**.
2. Adjunta `docs/metricas.csv` y pide: *Hazme un dashboard con el CSV adjunto: (1) minutos por fase, (2) intentos por fase, (3) cuántas fases acabaron en cada resultado, (4) minutos acumulados. Pon el SQL de cada gráfico visible y avisa de que los minutos son estimaciones. Si el dashboard no puede usar un archivo adjunto como fuente de datos, dímelo claramente en vez de inventar datos.*
3. Con un almacén de datos (BigQuery, Snowflake, Redshift...) conectado sí ejecutaría SQL real: `dashboard/metricas.sql` trae la tabla y las consultas.

## Conectores de la cuenta (vistos en la pantalla, sin tocarlos)
Google Calendar, Google Drive, Notion y Claude in Chrome activos; Stripe pide atención. Ningún almacén de datos.

## Para borrarlo
Chat «Dashboard de métricas CSV» en la barra lateral → menú → Eliminar.
