# Submission checklist — due 24 October 2026

Repository: https://github.com/Swagata-Bhowmik/group4-mlflow-capstone ·
Live dashboard: https://group4-mlflow-capstone.onrender.com/

## Deliverables (brief section 6)

| Deliverable | Where | Status |
|---|---|---|
| Repository: pipeline, configuration, tests, workflows, Dockerfile, README | `capstone/`, `config.yaml`, `tests/`, `.github/workflows/`, `Dockerfile`, `deploy/render/Dockerfile`, `README.md` | Done |
| Design note (≤ 2 pages) with architecture diagram | `output/pdf/design_note.pdf` | Done |
| Workflow graph, run history and registry screenshots | `output/screenshots/01_…`, `02_…`, `03_…`, `04_…` (index: `output/screenshots/README.md`) | Done |
| Evidence of two failing-gate scenarios | `reports/live_safe_failures.json` (real HTTP server), `reports/safe_failures.json` (in-process), failed runs in `02_mlflow_run_history.png`, PR #2 | Done |
| Lineage demonstration (live) | Dashboard **Lineage** tab, `/lineage`, `05_live_lineage.png`, `04_mlflow_run_detail.png` | Done — show live in the demo |
| CI history incl. at least one release | GitHub Actions; PR #1 and #3 passed, PR #2 failed then passed; releases `build-<sha>`; screenshots `20_…` to `24_…` | Done |
| Monitoring dashboard or report, three batches | Dashboard **Monitoring** tab, `reports/monitoring.html`, `reports/monitoring.json`, `14_dashboard_monitoring.png` | Done |
| 5–10 minute demonstration | Script: `docs/DEMO.md` | **To do by the team: rehearse and record** |
| Reflection (1 page) | `output/pdf/reflection.pdf` | Done — both read it and agree with it |

## Acceptance criteria evidence (brief section 5)

| Task | Evidence |
|---|---|
| 1 Framing | Numeric, justified thresholds and lifecycle mapping: design note §01–02 |
| 2 Reproducibility | `reports/fresh_clone_reproduction.json` (clean clone + locked install, MAE within 1e-6); config validated on load (`capstone/config.py`) |
| 3 Pipeline | `STAGES` in `capstone/core.py` = Pipeline tab; per-stage logs in `state/runs/*/run.json` and MLflow; `python -m capstone stage <name> --run <dir>` |
| 4 Gates | Bad data → validate, bad model → evaluate, endpoint unchanged: `reports/live_safe_failures.json`; thresholds in `config.yaml` |
| 5 Tracking/lineage | MLflow runs, registry aliases/tags; live `/lineage` |
| 6 CI/CD | `ci.yml` (PR), `release.yml` (main → image tagged with SHA → release → Render), rollback tested: `reports/render_rollback.json`, procedure in `docs/OPERATIONS.md` |
| 7 Serving/monitoring | `/metrics`, Operations tab, `reports/load_test.json`, monitoring report with alert rules and responses |
| 8 Demo | `docs/DEMO.md` |

## Before submitting

- [ ] Both students rehearse `docs/DEMO.md` and record 5–10 minutes, each explaining a part.
- [ ] Open the live dashboard shortly before the demo (free host wakes in ~1 minute).
- [ ] Check every link in the PDFs and README opens.
- [ ] Upload `group4_capstone_submission.zip` (built by `scripts/build_submission.sh`) plus the recording, through the professor's channel.

## Honest limits to mention if asked

- Render Free: one worker, sleeps when idle, no persistent state; every build retrains, so the
  incumbent comparison across releases is proven locally, not on Render.
- Latency target (p95 ≤ 200 ms) is **not** met with 5 concurrent clients on the free host; errors were 0.
- Prometheus/Grafana are configured for a Docker host (`compose.yaml`) but were not run on a
  persistent host; the dashboard and `/metrics` provide the live operational view.
- Public API has no authentication.
