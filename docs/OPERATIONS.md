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

## Live service rollback on Render (procedure)

Every commit that passed *Build and release* has a GitHub release `build-<full sha>` and a Docker Hub
image tagged with the same SHA, so "the previous version" is always identifiable.

1. Find the commit to return to: GitHub → Releases (or `reports/render_auto_deployment.json`), and note
   the currently live commit from https://group4-mlflow-capstone.onrender.com/lineage (`source.commit`).
2. GitHub → Actions → **Roll back Render deployment** → *Run workflow* on `main`, paste the full
   40-character SHA of the earlier release.
3. The workflow refuses a commit without a `build-<sha>` release, asks Render to deploy exactly that
   commit, waits for it to go live and fails unless public `/health` is OK and `/lineage` reports that
   commit. The Render build reruns the gated pipeline for that commit.
4. Verify yourself: `/lineage` commit, a known `/predict` request, and the dashboard.
5. Roll forward by running the same workflow with the newer SHA, or by merging the fix to `main`.

Recorded test: `reports/render_rollback.json` (produced by `scripts/render_rollback_test.py`, which
dispatches the workflow twice and checks live lineage after each step).

## Compose host rollback (prepared, not executed)

For a self-hosted Docker host: set `CAPSTONE_IMAGE=DOCKERHUB_USERNAME/group4-mlflow-capstone@sha256:RELEASE_DIGEST`
and run `bash scripts/deploy.sh`. If candidate gates fail, the script stops before recreating the API; if
new containers fail health checks it attempts model rollback and restores the previous image. Keep the
named model-state volume (never `docker compose down -v` on demonstration state). This path has not been
executed on a real Docker host.

## Alert responses

- Input shift only: investigate collection/market changes and affected segments, retain model, consider a candidate retraining run.
- Error increase with labels: investigate performance by segment, schedule candidate training, require absolute and incumbent gates before promotion. Do not train automatically on these monitoring batches in the current demonstration.
- Rising HTTP errors: separate invalid client payloads from service failures; correct client schema or restore the last healthy service.
- Latency: examine load and resources; `scripts/load_test.py` repeats the documented workload. On Render Free, p95 exceeded 200 ms with 5 concurrent clients (`reports/load_test.json`); scale CPU/workers before relying on it.
- Model age >30 days: review current accuracy and new data, then schedule gated retraining.

## Limitations and scope

This local workflow intentionally uses one worker and POSIX filesystem locks. It has no distributed scheduler, retries, multi-host lock, authentication, high-availability database, or outbound notifications. Registry labels are descriptive; the API follows the serving manifest. Compare alias and manifest after interrupted promotions. Source snapshots and hashes support current local provenance; GitHub history and deployed commit lineage are now verified; see ../CLAUDE.md. Paths in saved local manifests must be regenerated for a different computer/container.
