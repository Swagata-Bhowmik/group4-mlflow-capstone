# Submission checklist — 22 October 2026

Current project context: [../CLAUDE.md](../CLAUDE.md). The assignment is not yet fully ready for final submission.

## Completed and evidenced

- [x] Supplied data audited, hashes recorded, leakage-safe preprocessing and model comparison.
- [x] Held-out final evaluation: MAE 5.77518 lakhs; RMSE 7.50646 lakhs.
- [x] Eight-stage persisted workflow, reruns/logs, artifact integrity, MLflow tracking/registry.
- [x] Local absolute/incumbent gates and safe bad-data/bad-model failure demonstrations.
- [x] Local model rollback through in-process API checks.
- [x] Three-batch drift/performance reports and configured operational alerts.
- [x] GitHub repository and six initial AI-assisted import commits with both identities.
- [x] Tests, dependency installation, Docker build and network container health passed in CI.
- [x] Docker Hub images and GitHub releases published.
- [x] Public Render Free API deployed; health, predictions, docs, lineage and metrics checked.
- [x] Automatic main-branch deployment verified for b608040; release and deploy-render jobs passed.
- [x] Real deployed source commit recorded in public model lineage.
- [x] Two-page design and one-page reflection PDFs exist (need final refresh).

## Required before final submission

- [ ] Safely reconcile local Git with remote and publish latest handoff/evidence.
- [ ] Create genuine passing and intentional failing PR checks; fix and retain CI history.
- [ ] Run full Compose monitoring services and capture real workflow/run/registry/dashboard screenshots.
- [ ] Demonstrate safe-failure continuity against the actual network endpoint.
- [ ] Demonstrate real deployed model/container/image rollback and capture evidence.
- [ ] Document network latency, throughput and errors under a defined workload.
- [ ] Record fresh-clone reproduction explicitly. CI fresh installs have passed, but the older reproduction.json used the existing interpreter.
- [ ] Refresh PDFs for actual cloud architecture and limitations; rebuild the stale submission ZIP.
- [ ] Rehearse/record the 5–10 minute demonstration with both students explaining/modifying the project.
- [ ] Confirm professor's deadline/portal and submit.

## Evidence boundaries

Render Free hosts an API with model state baked into each build. It does not host the full persistent MLflow/Prometheus/Grafana stack; runtime changes do not persist. Model state starts fresh on each build, so cross-release incumbent comparison on Render is not established. Do not label local TestClient benchmarks as network load tests or local model rollback as deployed-image rollback.

See reports/render_auto_deployment.json for the verified automatic deployment; reports/render_deployment.json describes the earlier initial deployment. Historical local reports remain valid for their stated execution environment.
