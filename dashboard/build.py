#!/usr/bin/env python3
"""Phase 7b, option B: local, open dashboard of the exercise metrics. No external services.

Loads docs/metrics.csv (and, if it exists, experiment/phase7/results.json) into SQLite, runs one SQL query per chart and writes
dashboard/index.html with Chart.js (local file chart.umd.js, no CDN). Each chart's query is shown below it.

Usage: python3 dashboard/build.py        ->   dashboard/index.html
Data honesty: the 'minutes' are ESTIMATES from the session, not timed; there are few rows (this is not statistics).
"""
import csv, html, json, pathlib, sqlite3

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE metrics (position INTEGER, date TEXT, phase TEXT, model TEXT, minutes REAL, attempts INTEGER, result TEXT, notes TEXT)")
rows = list(csv.reader((ROOT / "docs/metrics.csv").open(encoding="utf-8")))[1:]
db.executemany("INSERT INTO metrics VALUES (?,?,?,?,?,?,?,?)", [(i, f[0], f[1], f[2], float(f[3]), int(f[4]), f[5], f[6]) for i, f in enumerate(rows, 1)])
# 'family' groups the model names (Sonnet, local Qwen, Opus...) so they can be compared
db.execute("""CREATE VIEW m AS SELECT *, CASE WHEN model LIKE '%qwen%' OR model LIKE '%gemma%' THEN 'Local (Ollama)'
                                              WHEN model LIKE '%Opus%' THEN 'Opus 5.5 (cloud)' WHEN model LIKE '%Sonnet%' THEN 'Sonnet 5.5 (cloud)' ELSE model END AS family FROM metrics""")

exp_path = ROOT / "experiment/phase7/results.json"
has_exp = exp_path.exists()
if has_exp:
    db.execute("CREATE TABLE experiment (participant TEXT, model TEXT, passed INTEGER, total INTEGER, requirements TEXT, quality TEXT, seconds REAL, turns INTEGER, cost_usd REAL, notes TEXT)")
    for r in json.loads(exp_path.read_text(encoding="utf-8")):
        db.execute("INSERT INTO experiment VALUES (?,?,?,?,?,?,?,?,?,?)", (r["participant"], r["model"], r["passed"], r["total"], r["requirements"], r["quality"], r["seconds"], r.get("turns"), r.get("cost_usd"), r.get("notes", "")))

CHARTS = [
    dict(id="minutes", title="Minutes per phase (estimated)", type="bar", sql="SELECT phase, SUM(minutes) AS minutes\nFROM m\nGROUP BY phase\nORDER BY MIN(position);"),
    dict(id="attempts", title="Attempts until accepted, per phase", type="bar", sql="SELECT phase, SUM(attempts) AS attempts\nFROM m\nGROUP BY phase\nORDER BY MIN(position);"),
    dict(id="result", title="Result of each phase", type="doughnut", sql="SELECT result, COUNT(*) AS phases\nFROM m\nGROUP BY result;"),
    dict(id="cumulative", title="Cumulative effort (minutes) over the exercise", type="line", sql="SELECT phase,\n       SUM(minutes) OVER (ORDER BY position) AS cumulative_minutes\nFROM m\nORDER BY position;"),
]
if has_exp:
    CHARTS += [
        dict(id="exp_points", title="Experiment (same task, same evaluator): % of checks passed (requirements + extra quality)", type="bar", sql="SELECT participant, ROUND(100.0 * passed / total, 1) AS pct_passed\nFROM experiment\nORDER BY pct_passed DESC;"),
        dict(id="exp_time", title="Experiment: seconds until finished", type="bar", sql="SELECT participant, ROUND(seconds, 0) AS seconds\nFROM experiment\nORDER BY seconds;"),
    ]
data = {}
for g in CHARTS:
    cur = db.execute(g["sql"])
    cols = [d[0] for d in cur.description]
    rows_g = cur.fetchall()
    data[g["id"]] = dict(labels=[str(f[0]) for f in rows_g], values=[f[1] for f in rows_g], column=cols[1])

table = db.execute("SELECT phase, family, minutes, attempts, result, notes FROM m ORDER BY position").fetchall()
table_exp = db.execute("SELECT participant, model, requirements, quality, seconds, turns, cost_usd, notes FROM experiment").fetchall() if has_exp else []
totals = db.execute("SELECT SUM(minutes), SUM(attempts), COUNT(*) FROM m").fetchone()


def row_html(cells):
    return "<tr>" + "".join(f"<td>{html.escape('' if c is None else str(c))}</td>" for c in cells) + "</tr>"


cards = "".join(
    f'<section class="card"><h2>{html.escape(g["title"])}</h2><div class="canvas-box"><canvas id="c_{g["id"]}"></canvas></div>'
    f'<details><summary>SQL query for this chart</summary><pre>{html.escape(g["sql"])}</pre></details></section>' for g in CHARTS)
template = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard · lamp studio</title>
<style>
:root{--bg:#0f1115;--surface:#1a1d24;--text:#f4f1ea;--soft:rgba(244,241,234,.68);--accent:#ffb703;--border:rgba(244,241,234,.14)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 -apple-system,"Helvetica Neue",Arial,sans-serif;padding:32px 20px 60px}
main{max-width:1180px;margin:0 auto}h1{font-size:34px;margin:0 0 6px;letter-spacing:-.02em}.sub{color:var(--soft);margin:0 0 22px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:22px}.kpi{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:14px 16px}
.kpi b{display:block;font-size:30px;color:var(--accent);line-height:1.1}.kpi span{color:var(--soft);font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:16px}@media(max-width:560px){.grid{grid-template-columns:1fr}}
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px 18px}.card h2{font-size:16px;margin:0 0 10px}
.canvas-box{position:relative;height:280px}details{margin-top:10px;color:var(--soft);font-size:13px}summary{cursor:pointer}
pre{margin:8px 0 0;padding:10px;background:#0b0d11;border-radius:8px;overflow:auto;color:#cfe3ff;font:12px/1.45 ui-monospace,Menlo,monospace}
h3{margin:28px 0 8px;font-size:18px}.table{overflow:auto;border:1px solid var(--border);border-radius:12px}table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--border);vertical-align:top}th{color:var(--accent);font-weight:600;white-space:nowrap}td:last-child{min-width:260px;color:var(--soft)}
.notice{margin-top:26px;padding:14px 16px;border-left:3px solid var(--accent);background:rgba(255,183,3,.07);color:var(--soft);font-size:14px;border-radius:0 10px 10px 0}
</style></head><body><main>
<h1>Lamp studio</h1><p class="sub">Exercise metrics, generated from <code>docs/metrics.csv</code> with SQLite and Chart.js (all local).</p>
<div class="kpis"><div class="kpi"><b>__ROWS__</b><span>logged attempts</span></div><div class="kpi"><b>__MIN__</b><span>estimated minutes</span></div><div class="kpi"><b>__ATT__</b><span>attempts summed</span></div></div>
<div class="grid">__CARDS__</div>
__EXPERIMENT__
<h3>All rows</h3><div class="table"><table><thead><tr><th>Phase</th><th>Model</th><th>Min</th><th>Attempts</th><th>Result</th><th>Notes</th></tr></thead><tbody>__TABLE__</tbody></table></div>
<p class="notice"><b>Read it carefully.</b> The minutes are <b>estimates</b> from the session, not timed. Almost all rows are from the same model (Sonnet 5.5 in the cloud) and the local model's rows are for different tasks, so they CANNOT be compared with each other: the only valid comparison between models is the Phase 7 experiment (same task, same prompt, same evaluator, a single attempt per model). There is little data: it shows where the work was hard, not statistics.</p>
</main>
<script src="chart.umd.js"></script>
<script>
const DATA = __DATA__, TYPES = __TYPES__;
const ACCENT = "#ffb703", PALETTE = ["#ffb703", "#7fd1b9", "#8ab4ff", "#ff7a59", "#c98f5a", "#b69cff"];
Chart.defaults.color = "rgba(244,241,234,.75)"; Chart.defaults.borderColor = "rgba(244,241,234,.12)"; Chart.defaults.font.family = "-apple-system,Helvetica Neue,Arial,sans-serif";
for (const [id, type] of Object.entries(TYPES)) {
  const d = DATA[id], circular = type === "doughnut";
  new Chart(document.getElementById("c_" + id), { type: type,
    data: { labels: d.labels, datasets: [{ label: d.column, data: d.values, backgroundColor: circular ? PALETTE : ACCENT, borderColor: circular ? "#1a1d24" : ACCENT, tension: .25, fill: false }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: circular } }, scales: circular ? {} : { y: { beginAtZero: true, title: { display: true, text: d.column } } } } });
}
</script></body></html>"""

exp_html = ""
if has_exp:
    exp_html = ('<h3>Phase 7 experiment: the same task with each model</h3><div class="table"><table><thead><tr><th>Participant</th><th>Model</th><th>Prompt requirements</th><th>Extra quality</th><th>Seconds</th><th>Turns</th><th>Cost (USD)</th><th>Notes</th></tr></thead><tbody>'
                + "".join(row_html([p, m, rq, q, sec, tu, c, n]) for p, m, rq, q, sec, tu, c, n in table_exp) + "</tbody></table></div>")
output = (template.replace("__CARDS__", cards).replace("__TABLE__", "".join(row_html(f) for f in table)).replace("__EXPERIMENT__", exp_html)
          .replace("__ROWS__", str(totals[2])).replace("__MIN__", f"{totals[0]:.0f}").replace("__ATT__", str(totals[1]))
          .replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__TYPES__", json.dumps({g["id"]: g["type"] for g in CHARTS})))
(HERE / "index.html").write_text(output, encoding="utf-8")
print(f"OK dashboard/index.html: {len(CHARTS)} charts, {totals[2]} rows" + (f", {len(table_exp)} experiment participants" if has_exp else ""))


# ---- SQL export for a data warehouse (BigQuery, Snowflake, Redshift, ClickHouse, Databricks...). Standard SQL.
def sql_quote(v):
    return "'" + str(v).replace("'", "''") + "'"


values = ",\n".join(
    "  (" + ", ".join([str(i), sql_quote(f[0]), sql_quote(f[1]), sql_quote(f[2]), f[3], f[4], sql_quote(f[5]), sql_quote(f[6])]) + ")"
    for i, f in enumerate(rows, 1))
queries = "\n".join(f"-- {i}) {g['title']}\n{g['sql'].replace(' m', ' study_metrics').replace(chr(10), ' ')}" for i, g in enumerate(CHARTS[:4], 1))
(HERE / "metrics.sql").write_text(
    "-- Lamp studio metrics, ready to load into a data warehouse (BigQuery, Snowflake, Redshift, ClickHouse, Databricks...).\n"
    "-- Standard SQL. Generated from docs/metrics.csv by dashboard/build.py. The minutes are ESTIMATES.\n"
    "CREATE TABLE study_metrics (\n  position INTEGER, date VARCHAR(10), phase VARCHAR(20), model VARCHAR(120),\n"
    "  minutes DOUBLE PRECISION, attempts INTEGER, result VARCHAR(20), notes VARCHAR(2000)\n);\n"
    "INSERT INTO study_metrics (position, date, phase, model, minutes, attempts, result, notes) VALUES\n" + values + ";\n\n"
    "-- The queries of each chart in the local dashboard (dashboard/index.html), over the study_metrics table:\n" + queries + "\n", encoding="utf-8")
