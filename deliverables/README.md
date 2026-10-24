# 📦 Deliverables — Group 4

**Project 4 · Capstone: End-to-End MLflow Pipeline from Raw Data to Monitored Deployment**
Swagata Bhowmik (B053) · Sumit Kothari (B062) · Elective II: Machine Learning Operations · Dr. Santosh Kumar

**Live dashboard:** https://group4-mlflow-capstone.onrender.com/ · **Repository:** https://github.com/Swagata-Bhowmik/group4-mlflow-capstone
(The free host may take about a minute to wake up after being idle.)

| # | Deliverable | Files |
|:---:|---|---|
| 1 | **Repository** with pipeline, configuration, tests, workflows, Dockerfile and README | The repository itself — start with the [README](../README.md) |
| 2 | **Design note** (2 pages) with architecture diagram | [01_design_note/design_note.pdf](01_design_note/design_note.pdf) |
| 3 | **Workflow graph, run history and registry screenshots** | [02_workflow_run_history_registry/](02_workflow_run_history_registry/) |
| 4 | **Evidence of two failing-gate scenarios** | [03_failing_gate_evidence/](03_failing_gate_evidence/) · [Pull Request #2](https://github.com/Swagata-Bhowmik/group4-mlflow-capstone/pull/2) |
| 5 | **Lineage demonstration** | [04_lineage/](04_lineage/) · live: [Lineage tab](https://group4-mlflow-capstone.onrender.com/#lineage) and [/lineage](https://group4-mlflow-capstone.onrender.com/lineage) |
| 6 | **CI history including releases** | [05_ci_history_and_releases/](05_ci_history_and_releases/) · [Actions](https://github.com/Swagata-Bhowmik/group4-mlflow-capstone/actions) · [Releases](https://github.com/Swagata-Bhowmik/group4-mlflow-capstone/releases) |
| 7 | **Monitoring of the three incoming batches** | [06_monitoring/](06_monitoring/) — open `monitoring.html` in a browser |
| 8 | **Reflection** (1 page) | [07_reflection/reflection.pdf](07_reflection/reflection.pdf) |
| 9 | **Demonstration video** | [08_demonstration/Group4_Project_Demo_Video.mp4](08_demonstration/Group4_Project_Demo_Video.mp4) |
| 10 | **Presentation** (12 slides) | [09_presentation/Group4_Presentation.pdf](09_presentation/Group4_Presentation.pdf) |
| 11 | **Project report** (Word and PDF) | [10_report/](10_report/) |

## What is in each folder

| Folder | Contents |
|---|---|
| `02_workflow_run_history_registry` | Workflow graph of the live run (8 stages, data gate, model gate); MLflow run history with passed and failed runs; MLflow registry (v1 production + champion, v2 archived); run detail with lineage tags |
| `03_failing_gate_evidence` | Bad data stopped at *validate* and bad model stopped at *evaluate* while a live server answered 115 requests with 0 errors (`live_safe_failures.json`); the same scenarios run in-process (`safe_failures.json`); invalid input rejected by the live API |
| `04_lineage` | Live model → MLflow run → Git commit → training-data SHA-256 → configuration (`live_lineage.json` captured from the live service) |
| `05_ci_history_and_releases` | Pull requests; PR #2 failing then fixed; GitHub Actions history; tested rollback of the live service (`render_rollback.json`); releases |
| `06_monitoring` | Three-batch drift and error report; dashboard Overview, Real listings, Monitoring and Operations tabs; network load test (`load_test.json`) |
