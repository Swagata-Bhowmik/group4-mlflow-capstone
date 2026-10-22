# 5–10 minute demonstration plan

Target length: 8 minutes. Both students must understand every part; the suggested speaking sequence is for presentation, not invented implementation ownership.

| Time | Show | Explain |
|---|---|---|
| 0:00–0:45 | Two-page design note | Asking-price objective, ₹ lakhs, average-error meaning, safe updates |
| 0:45–1:30 | `config.yaml` and workflow graph | Configured gates; training/validation/test separation |
| 1:30–2:30 | Real code change and GitHub PR checks | Tests + lightweight pipeline; show actual passing/failing PRs after Git setup |
| 2:30–3:30 | Pipeline logs and MLflow UI | Eight stages, run metrics, source/data/config lineage |
| 3:30–4:30 | `/predict`, `/health`, `/lineage` | Model version and traceability; perform one prediction |
| 4:30–5:45 | Monitoring HTML and Grafana | Batch 2 input shift differs from Batch 3 accuracy deterioration |
| 5:45–7:00 | `python -m capstone demo` | Bad data and bad model rejected; same response/version preserved; rollback |
| 7:00–8:00 | Reflection and evidence checklist | Explain limits honestly, propose improvements |

Before recording, review `SUBMISSION.md`. GitHub CI, Docker publishing and the Render API are verified; full monitoring screenshots, network failure/rollback evidence, and team rehearsal still need completion. Avoid showing tokens or private environment variables.

## Questions both presenters should answer

1. Why median imputation fits only training rows, and why IDs are excluded.
2. Why Ridge was selected over the larger models on validation data.
3. What MAE in lakhs means, and why RMSE is also logged.
4. Why a data shift can occur without breaking min/max checks or prediction quality.
5. How each gate protects the current model; what happens on the first deployment.
6. How to rerun evaluate without retraining, and why altered artifacts are rejected.
7. How the deployed model links to code, configuration, data, and an MLflow run.
8. Why aliases/lifecycle tags replace legacy MLflow stages.
9. What rollback restores and which parts have actually been tested.
10. How the final test differs from validation and monitored incoming data.

Practice making a small legitimate configuration change, explaining its impact, and restoring it. Do not change thresholds solely to claim a passing result. Demonstrate the intentional dummy-model failure using its isolated demo configuration.
