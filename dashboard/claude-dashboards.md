# Option A: Claude Dashboards (claude.ai) with the studio's metrics

## Result (tested on 15 Oct 2026, with the Claude extension in Chrome)
- **It was done.** In the user's account (Pro plan) the dashboard **"Métricas del ejercicio"** was created by attaching `docs/metrics.csv` to the chat of the Dashboard template (Beta):
  (private: "Share" was not pressed). Chat: "Dashboard de métricas CSV".
- **It has** 3 indicators (748.2 min · 47 attempts · 13 phases) and 4 charts (minutes per phase, attempts per phase, phases per result, cumulative minutes), each with its "equivalent SQL".
- **It matches option B** (`dashboard/index.html`): same figures.

## What I had assumed wrongly
I had written that a CSV "could not be used directly" as a source, because the help page only mentions data warehouses and connected apps (Salesforce...).
**It was false in practice:** attaching the CSV to the chat works. But there is a nuance that Claude declared (I asked for it in the message):
> "This dashboard does not run SQL on the attached file. It reads the CSV and aggregates in the browser. The SQL of each chart is the equivalent query." (and it checked that it gives the same figures in SQLite)

That is: it is a **static dashboard over the uploaded CSV** (it does not refresh from a live source), and its "SQL" is explanatory, not the one that is executed.

## Differences worth knowing
- "Phases per result": Claude counts **distinct phases** (12 ok, 1 partial); `dashboard/index.html` counts **rows** (each logged attempt), which is why their figures differ.
- The minutes are estimates (the dashboard says so); with 15 rows it is not statistics.
- To **update it** you have to attach the new CSV in the chat again (it does not refresh by itself).
- It spends plan usage quota (a response of about 2-3 minutes with Sonnet 5.5).

## How to repeat it
1. claude.ai → Artifacts → **+** → **Dashboard (Beta)**.
2. Attach `docs/metrics.csv` and ask: *Make me a dashboard with the attached CSV: (1) minutes per phase, (2) attempts per phase, (3) how many phases ended in each result, (4) cumulative minutes. Make the SQL of each chart visible and warn that the minutes are estimates. If the dashboard cannot use an attached file as a data source, tell me clearly instead of inventing data.*
3. With a data warehouse (BigQuery, Snowflake, Redshift...) connected it would indeed run real SQL: `dashboard/metrics.sql` brings the table and the queries.

## Account connectors (seen on screen, without touching them)
Google Calendar, Google Drive, Notion and Claude in Chrome active; Stripe asks for attention. No data warehouse.

## To delete it
Chat "Dashboard de métricas CSV" in the sidebar → menu → Delete.
