#!/usr/bin/env python3
"""Fase 7b, opción B: dashboard local y abierto de las métricas del ejercicio. Sin servicios externos.

Carga docs/metricas.csv (y, si existe, experimento/fase7/resultados.json) en SQLite, ejecuta una consulta SQL por gráfico y escribe
dashboard/index.html con Chart.js (archivo local chart.umd.js, sin CDN). La consulta de cada gráfico se muestra debajo de él.

Uso: python3 dashboard/construir.py        ->   dashboard/index.html
Honestidad de los datos: los 'minutos' son ESTIMACIONES de la sesión, no cronometrados; son pocas filas (no es estadística).
"""
import csv, html, json, pathlib, sqlite3

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE metricas (orden INTEGER, fecha TEXT, fase TEXT, modelo TEXT, minutos REAL, intentos INTEGER, resultado TEXT, notas TEXT)")
filas = list(csv.reader((RAIZ / "docs/metricas.csv").open(encoding="utf-8")))[1:]
db.executemany("INSERT INTO metricas VALUES (?,?,?,?,?,?,?,?)", [(i, f[0], f[1], f[2], float(f[3]), int(f[4]), f[5], f[6]) for i, f in enumerate(filas, 1)])
# 'familia' agrupa los nombres de modelo (Sonnet, Qwen local, Opus...) para poder compararlos
db.execute("""CREATE VIEW m AS SELECT *, CASE WHEN modelo LIKE '%qwen%' OR modelo LIKE '%gemma%' THEN 'Local (Ollama)'
                                              WHEN modelo LIKE '%Opus%' THEN 'Opus 5.5 (nube)' WHEN modelo LIKE '%Sonnet%' THEN 'Sonnet 5.5 (nube)' ELSE modelo END AS familia FROM metricas""")

exp_ruta = RAIZ / "experimento/fase7/resultados.json"
tiene_exp = exp_ruta.exists()
if tiene_exp:
    db.execute("CREATE TABLE experimento (participante TEXT, modelo TEXT, aprobadas INTEGER, total INTEGER, requisitos TEXT, calidad TEXT, segundos REAL, turnos INTEGER, coste_usd REAL, notas TEXT)")
    for r in json.loads(exp_ruta.read_text(encoding="utf-8")):
        db.execute("INSERT INTO experimento VALUES (?,?,?,?,?,?,?,?,?,?)", (r["participante"], r["modelo"], r["aprobadas"], r["total"], r["requisitos"], r["calidad"], r["segundos"], r.get("turnos"), r.get("coste_usd"), r.get("notas", "")))

GRAFICOS = [
    dict(id="minutos", titulo="Minutos por fase (estimados)", tipo="bar", sql="SELECT fase, SUM(minutos) AS minutos\nFROM m\nGROUP BY fase\nORDER BY MIN(orden);"),
    dict(id="intentos", titulo="Intentos hasta darlo por bueno, por fase", tipo="bar", sql="SELECT fase, SUM(intentos) AS intentos\nFROM m\nGROUP BY fase\nORDER BY MIN(orden);"),
    dict(id="resultado", titulo="Resultado de cada fase", tipo="doughnut", sql="SELECT resultado, COUNT(*) AS fases\nFROM m\nGROUP BY resultado;"),
    dict(id="acumulado", titulo="Esfuerzo acumulado (minutos) a lo largo del ejercicio", tipo="line", sql="SELECT fase,\n       SUM(minutos) OVER (ORDER BY orden) AS minutos_acumulados\nFROM m\nORDER BY orden;"),
]
if tiene_exp:
    GRAFICOS += [
        dict(id="exp_puntos", titulo="Experimento (misma tarea, mismo evaluador): % de comprobaciones superadas (requisitos + calidad extra)", tipo="bar", sql="SELECT participante, ROUND(100.0 * aprobadas / total, 1) AS pct_superado\nFROM experimento\nORDER BY pct_superado DESC;"),
        dict(id="exp_tiempo", titulo="Experimento: segundos hasta terminar", tipo="bar", sql="SELECT participante, ROUND(segundos, 0) AS segundos\nFROM experimento\nORDER BY segundos;"),
    ]
datos = {}
for g in GRAFICOS:
    cur = db.execute(g["sql"])
    cols = [d[0] for d in cur.description]
    filas_g = cur.fetchall()
    datos[g["id"]] = dict(etiquetas=[str(f[0]) for f in filas_g], valores=[f[1] for f in filas_g], columna=cols[1])

tabla = db.execute("SELECT fase, familia, minutos, intentos, resultado, notas FROM m ORDER BY orden").fetchall()
tabla_exp = db.execute("SELECT participante, modelo, requisitos, calidad, segundos, turnos, coste_usd, notas FROM experimento").fetchall() if tiene_exp else []
totales = db.execute("SELECT SUM(minutos), SUM(intentos), COUNT(*) FROM m").fetchone()


def fila_html(celdas):
    return "<tr>" + "".join(f"<td>{html.escape('' if c is None else str(c))}</td>" for c in celdas) + "</tr>"


tarjetas = "".join(
    f'<section class="tarjeta"><h2>{html.escape(g["titulo"])}</h2><div class="lienzo"><canvas id="c_{g["id"]}"></canvas></div>'
    f'<details><summary>Consulta SQL de este gráfico</summary><pre>{html.escape(g["sql"])}</pre></details></section>' for g in GRAFICOS)
plantilla = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard · estudio de la lámpara</title>
<style>
:root{--fondo:#0f1115;--sup:#1a1d24;--texto:#f4f1ea;--suave:rgba(244,241,234,.68);--acento:#ffb703;--borde:rgba(244,241,234,.14)}
*{box-sizing:border-box}body{margin:0;background:var(--fondo);color:var(--texto);font:16px/1.5 -apple-system,"Helvetica Neue",Arial,sans-serif;padding:32px 20px 60px}
main{max-width:1180px;margin:0 auto}h1{font-size:34px;margin:0 0 6px;letter-spacing:-.02em}.sub{color:var(--suave);margin:0 0 22px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:22px}.kpi{background:var(--sup);border:1px solid var(--borde);border-radius:12px;padding:14px 16px}
.kpi b{display:block;font-size:30px;color:var(--acento);line-height:1.1}.kpi span{color:var(--suave);font-size:13px}
.rejilla{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:16px}@media(max-width:560px){.rejilla{grid-template-columns:1fr}}
.tarjeta{background:var(--sup);border:1px solid var(--borde);border-radius:14px;padding:16px 18px}.tarjeta h2{font-size:16px;margin:0 0 10px}
.lienzo{position:relative;height:280px}details{margin-top:10px;color:var(--suave);font-size:13px}summary{cursor:pointer}
pre{margin:8px 0 0;padding:10px;background:#0b0d11;border-radius:8px;overflow:auto;color:#cfe3ff;font:12px/1.45 ui-monospace,Menlo,monospace}
h3{margin:28px 0 8px;font-size:18px}.tabla{overflow:auto;border:1px solid var(--borde);border-radius:12px}table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--borde);vertical-align:top}th{color:var(--acento);font-weight:600;white-space:nowrap}td:last-child{min-width:260px;color:var(--suave)}
.aviso{margin-top:26px;padding:14px 16px;border-left:3px solid var(--acento);background:rgba(255,183,3,.07);color:var(--suave);font-size:14px;border-radius:0 10px 10px 0}
</style></head><body><main>
<h1>Estudio creativo de la lámpara</h1><p class="sub">Métricas del ejercicio, generadas desde <code>docs/metricas.csv</code> con SQLite y Chart.js (todo local).</p>
<div class="kpis"><div class="kpi"><b>__FILAS__</b><span>intentos registrados</span></div><div class="kpi"><b>__MIN__</b><span>minutos estimados</span></div><div class="kpi"><b>__INT__</b><span>intentos sumados</span></div></div>
<div class="rejilla">__TARJETAS__</div>
__EXPERIMENTO__
<h3>Todas las filas</h3><div class="tabla"><table><thead><tr><th>Fase</th><th>Modelo</th><th>Min</th><th>Intentos</th><th>Resultado</th><th>Notas</th></tr></thead><tbody>__TABLA__</tbody></table></div>
<p class="aviso"><b>Léelo con cuidado.</b> Los minutos son <b>estimaciones</b> de la sesión, no cronometrados. Casi todas las filas son del mismo modelo (Sonnet 5.5 en la nube) y las del modelo local son de tareas distintas, así que NO se pueden comparar entre sí: la única comparación entre modelos válida es el experimento de la Fase 7 (misma tarea, mismo prompt, mismo evaluador, un solo intento por modelo). Son pocos datos: sirven para ver dónde costó trabajo, no para sacar estadísticas.</p>
</main>
<script src="chart.umd.js"></script>
<script>
const DATOS = __DATOS__, TIPOS = __TIPOS__;
const ACENTO = "#ffb703", PALETA = ["#ffb703", "#7fd1b9", "#8ab4ff", "#ff7a59", "#c98f5a", "#b69cff"];
Chart.defaults.color = "rgba(244,241,234,.75)"; Chart.defaults.borderColor = "rgba(244,241,234,.12)"; Chart.defaults.font.family = "-apple-system,Helvetica Neue,Arial,sans-serif";
for (const [id, tipo] of Object.entries(TIPOS)) {
  const d = DATOS[id], circular = tipo === "doughnut";
  new Chart(document.getElementById("c_" + id), { type: tipo,
    data: { labels: d.etiquetas, datasets: [{ label: d.columna, data: d.valores, backgroundColor: circular ? PALETA : ACENTO, borderColor: circular ? "#1a1d24" : ACENTO, tension: .25, fill: false }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: circular } }, scales: circular ? {} : { y: { beginAtZero: true, title: { display: true, text: d.columna } } } } });
}
</script></body></html>"""

exp_html = ""
if tiene_exp:
    exp_html = ('<h3>Experimento de la Fase 7: la misma tarea con cada modelo</h3><div class="tabla"><table><thead><tr><th>Participante</th><th>Modelo</th><th>Requisitos del prompt</th><th>Calidad extra</th><th>Segundos</th><th>Turnos</th><th>Coste (USD)</th><th>Notas</th></tr></thead><tbody>'
                + "".join(fila_html([p, m, rq, cal, s, tu, c, n]) for p, m, rq, cal, s, tu, c, n in tabla_exp) + "</tbody></table></div>")
salida = (plantilla.replace("__TARJETAS__", tarjetas).replace("__TABLA__", "".join(fila_html(f) for f in tabla)).replace("__EXPERIMENTO__", exp_html)
          .replace("__FILAS__", str(totales[2])).replace("__MIN__", f"{totales[0]:.0f}").replace("__INT__", str(totales[1]))
          .replace("__DATOS__", json.dumps(datos, ensure_ascii=False)).replace("__TIPOS__", json.dumps({g["id"]: g["tipo"] for g in GRAFICOS})))
(AQUI / "index.html").write_text(salida, encoding="utf-8")
print(f"OK dashboard/index.html: {len(GRAFICOS)} gráficos, {totales[2]} filas" + (f", {len(tabla_exp)} participantes del experimento" if tiene_exp else ""))
