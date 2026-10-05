# Operations, recovery, and stage contracts

## Stage contracts

| Stage | Inputs | Persisted outputs | Failure behavior |
|---|---|---|---|
| ingest | Configured CSV | `raw.csv`, data hash manifest | No production change |
| validate | Raw snapshot + schema config | Stage validation record in `run.json` | Reject malformed, duplicate, excessive-missing, out-of-range records |
| features | Validated raw rows | Train/validation/test CSVs and feature contract | No fit on validation/test |
| train | Training CSV + model config | Fitted preprocessing/model joblib | No production change |
| evaluate | Candidate, validation CSV, current champion | Metrics and model hash in `evaluation.json` | Absolute or relative quality failure stops release |
| register | Passed evaluation and same model hash | MLflow version and `registration.json` | Candidate exists; champion unchanged |
| deploy | Validated registered model + unchanged champion | Immutable release, previous pointer, atomic production manifest | Pre-switch prediction failure leaves serving unchanged |
| monitor | Serving model, training reference, incoming batches | Batch JSON + HTML report | Alert/investigate; do not auto-promote |

All stages log start-derived duration, completion/failure, and artifacts into the local run record and MLflow. Downstream status is invalidated by rerunning an upstream stage. Artifact hashes are verified before consumers run. Independent reruns consume saved prerequisites. A rejected evaluation may be rerun after legitimate correction through upstream stages; do not weaken gates solely to force promotion.

## Model rollback (executed)

`python -m capstone rollback` restores `state/previous.json` through the same locked deployment code path, verifies artifact integrity, updates the registry alias and lifecycle tags, and atomically changes the serving pointer. Check `/health`, `/lineage`, and a known `/predict` request. The demo exercised a second valid release and restored the first; `reports/rollback.json` records the outcome. Running rollback a second time toggles back to the other saved release; inspect versions before doing so.

## Container release rollback (prepared, not executed)

Record the current immutable image tag before deployment. Set `CAPSTONE_IMAGE=DOCKERHUB_USERNAME/group4-mlflow-capstone@sha256:RELEASE_DIGEST` for the intended release and run `bash scripts/deploy.sh`. If candidate gates fail, the script stops before recreating the existing API. If new containers fail health checks, it attempts model rollback and restores the previously running image. First-ever deployment has no prior healthy release to restore; recover the deployment environment and rerun. Keep the named model-state volume; do not use `docker compose down -v` on the demonstration state.

For explicit recovery: inspect current/previous versions, run `docker compose --profile jobs run --rm pipeline python -m capstone rollback`, set the previous image tag, and use `docker compose up -d --wait api mlflow prometheus grafana`. Verify predictions and version. This part needs real Docker verification before claiming a tested container rollback.

## Alert responses

- Input shift only: investigate collection/market changes and affected segments, retain model, consider a candidate retraining run.
- Error increase with labels: investigate performance by segment, schedule candidate training, require absolute and incumbent gates before promotion. Do not train automatically on these monitoring batches in the current demonstration.
- Rising HTTP errors: separate invalid client payloads from service failures; correct client schema or restore the last healthy service.
- Latency: examine load and resources; benchmark before scaling. Local timing is not a throughput guarantee.
- Model age >30 days: review current accuracy and new data, then schedule gated retraining.

## Limitations and scope

This local workflow intentionally uses one worker and POSIX filesystem locks. It has no distributed scheduler, retries, multi-host lock, authentication, high-availability database, or outbound notifications. Registry labels are descriptive; the API follows the serving manifest. Compare alias and manifest after interrupted promotions. Source snapshots and hashes support current local provenance; commit lineage and version-controlled CSV history require the deferred Git setup. Paths in saved local manifests must be regenerated for a different computer/container.
