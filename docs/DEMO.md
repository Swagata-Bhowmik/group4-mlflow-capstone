# 5–10 minute demonstration script

Target: about 9 minutes. The brief asks for the full loop — **a code change, the CI run, the
pipeline run, deployment and the monitoring update, followed by one failure scenario** — with
**every team member explaining a part**. Speaker labels below are a suggestion: both of you must be
able to explain every part and make a small live change if asked.

**S** = Swagata · **K** = Sumit

## Before you press record (10 minutes before)

1. Open https://group4-mlflow-capstone.onrender.com/ once to wake the free server (can take ~1 minute).
2. In the project folder start MLflow: `.venv/bin/mlflow ui --backend-store-uri sqlite:///state/mlflow.db --port 5000`, open http://127.0.0.1:5000.
3. Open these GitHub tabs:
   [PR #2 (failed → fixed)](https://github.com/Swagata-Bhowmik/group4-mlflow-capstone/pull/2),
   [Actions](https://github.com/Swagata-Bhowmik/group4-mlflow-capstone/actions),
   [Releases](https://github.com/Swagata-Bhowmik/group4-mlflow-capstone/releases).
4. Keep a terminal open in the project folder. Close anything showing tokens or `.env` files.
5. For the live code change (step 3), prepare a one-line change on a branch in advance, for example
   the dashboard footer text or a new README line. A full merge-to-live cycle takes about 10–15
   minutes, so start it at the beginning of the recording and come back to it, or cut the wait.

## Script

| Time | Who | Show | Say (in your own words) |
|---|---|---|---|
| 0:00–0:45 | S | Dashboard **Overview** tab; design note page 1 | The start-up's problem; we predict asking price in lakhs; "on average within ±5.7 lakhs, about 9% of a typical listing"; safe automatic releases. |
| 0:45–1:45 | K | `config.yaml`; dashboard **Pipeline** tab | One validated YAML holds every path, threshold and hyperparameter. The eight stages are the `STAGES` list in `capstone/core.py`; the two dashed boxes are the data gate and model gate. Any stage can be rerun alone. |
| 1:45–3:15 | K | **Code change + CI:** PR #2 → its failed run → the fix | "I tried alpha 1000. CI ran the tests and the pipeline to the model gate: MAE 8.77 > 7, so the gate refused it. I reverted to alpha 10 and the checks passed." Then show your prepared live PR and its *Quality checks* run starting. |
| 3:15–4:30 | S | Merge → **Actions** *Build and release* run → Docker Hub tag → **Releases** → `deploy-render` log | Merge to main builds and tests a container, pushes an image tagged with the full commit SHA, creates a release, then deploys that exact commit to Render and checks live `/lineage`. The Render build itself runs the gated pipeline. |
| 4:30–5:15 | S | Dashboard **Lineage** tab; MLflow run page | "From the deployed model we can find its commit, MLflow run, data hash and configuration." Click the commit link to GitHub. In MLflow show the same run ID and its tags. |
| 5:15–5:45 | K | MLflow **Training runs** and **Registry** | Failed runs are kept with their metrics; registry versions carry `production`/`archived` tags and the `champion` alias, changed only by deploy/rollback. |
| 5:45–7:00 | K | **Monitoring** tab, then **Real listings** batch 3 | Monitoring update after deployment: batch 1 stable, batch 2 area drift only, batch 3 four drifting inputs and error doubled to 13.1 → alert. Draw batch 3 listings: dots fall below the diagonal. When an alert fires we keep serving and start a gated retraining run; nothing is promoted automatically. |
| 7:00–8:00 | S | **Failure scenario:** terminal `python scripts/live_safe_failure.py` (~20 s), then dashboard **Predict** → "Invalid: 0 bedrooms" | Bad data stops at *validate*, a dummy model stops at *evaluate*; the server kept answering (0 errors) with the same model version. Invalid input is rejected before reaching the model. |
| 8:00–8:30 | K | **Operations** tab; `reports/load_test.json` | 300 live requests, 0 errors; latency target missed with 5 parallel users on the free single-worker host — an honest limit. Rollback workflow: redeploys an earlier released commit and verifies lineage (`reports/render_rollback.json`). |
| 8:30–9:15 | S + K | Back to the live PR from step 3: show it deployed (Lineage tab commit changed, Pipeline tab "Started" time is new) | Close the loop; one sentence each on what you would improve (reflection). |

If something is slow on the free host, say so and continue; do not edit the recording to hide a failure.

## Questions both presenters should be ready for

1. Why median imputation is fitted on training rows only, and why `House_ID` and `Batch` are excluded.
2. Why Ridge (alpha 10) was chosen over gradient boosting and random forest on validation data.
3. What MAE in lakhs means for the founders, and why RMSE is also checked.
4. How input drift can happen without a performance alert (batch 2), and why batch 3 alerts.
5. How each gate protects the serving model, and what happens on the very first deployment.
6. How to rerun only `evaluate`, and why a changed upstream artifact is refused.
7. How the deployed model links to code, configuration, data and the MLflow run.
8. Why MLflow aliases and tags are used instead of the deprecated stages.
9. How to roll back the live service, and what exactly was tested.
10. Why the reserved test set is reported once and never used for choosing the model.

Practise one small legitimate live change each — for example, change `quality.max_mae` to 5.0 in a
throwaway copy of the config and run `python -m capstone --config <copy> run --stop-after evaluate`
to show the gate rejecting the model, then explain why you would not ship that threshold.
