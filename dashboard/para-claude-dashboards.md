# Opción A: Claude Dashboards (claude.ai) con las métricas del estudio

## Estado (comprobado el 15 de oct de 2026)
- **Disponible en tu plan Pro** (beta). Fuente: página de precios y ayuda de Anthropic.
- **Fuentes de datos documentadas:** almacenes (Amazon Redshift, BigQuery, ClickHouse, Databricks, Snowflake) y aplicaciones conectadas a Claude (el ejemplo de la ayuda es Salesforce).
- **No documentados como fuente:** CSV o archivos subidos, Google Drive, Notion, Supabase. Por eso `docs/metricas.csv` **no se puede usar directamente**. Si tu cuenta ofrece alguna de esas fuentes al crear el dashboard, vale; lo dice la propia pantalla.
- **No lo hice yo:** la extensión de Claude en Chrome no estaba conectada, y además necesitaría tus credenciales de un almacén.

## Pasos
1. En claude.ai, abre **Ajustes → Conectores** y mira qué fuentes de datos puedes conectar. Si ves un almacén o app de la lista, conéctalo.
2. Carga `dashboard/metricas.sql` en ese almacén (crea la tabla `metricas_estudio` con las 15 filas).
3. En un chat nuevo, elige **Output → Dashboards** (o pestaña **Artifacts** → plantilla Dashboards) y pega:

> Hazme un dashboard con la tabla `metricas_estudio`: (1) minutos por fase, (2) intentos por fase, (3) cuántas fases acabaron en cada resultado, (4) minutos acumulados a lo largo del ejercicio. Pon el SQL de cada gráfico visible. Avisa de que los minutos son estimaciones.

4. Cada gráfico muestra su consulta y cuándo se refrescó; para compartirlo, botón **Share** (empieza privado).

## Comparación con la opción B (local, ya hecha: `dashboard/index.html`)
La B funciona sin cuentas ni conectores, con Chart.js y SQLite; la A refresca desde una fuente viva y usa tu cuota de uso. Las consultas SQL son las mismas (`metricas.sql`, parte final).
