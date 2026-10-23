# Screenshots

| File | Shows |
|---|---|
| `01_workflow_graph_pipeline.png` | Workflow graph: the eight stages of the run behind the live model, both gates, model-gate checks |
| `02_mlflow_run_history.png` | MLflow run history: passed runs and failed gate runs with MAE/RMSE and the incumbent's MAE |
| `03_mlflow_registry.png` | MLflow registry: version 1 `production` + `champion` alias, version 2 `archived` |
| `04_mlflow_run_detail.png` | One run's metrics and lineage tags (code hash, commit, data hash, registered model) |
| `05_live_lineage.png` | Live lineage of the deployed model on the dashboard |
| `10_` to `15_dashboard_*.png` | Live dashboard: overview, prediction, rejected invalid input, real listings, monitoring, operations |
| `20_ci_pull_requests.png` | Pull requests #1 to #3 |
| `21_ci_pr2_failed_then_fixed.png` | PR #2: the alpha 1000 commit failed CI, the fix passed |
| `22_ci_actions_history.png` | GitHub Actions history: quality checks, releases, rollback runs |
| `23_rollback_workflow_run.png` | Successful "Roll back Render deployment" run |
| `24_releases.png` | GitHub releases created by the release workflow |

MLflow screenshots come from the local tracking database (`state/mlflow.db`). Dashboard and GitHub
screenshots were taken from the live sites on 22 and 23 October 2026.
