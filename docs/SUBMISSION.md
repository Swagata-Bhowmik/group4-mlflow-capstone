# Submission evidence and remaining external steps

## Completed locally

- [x] Supplied data preserved, parsed, and profiled; hashes recorded.
- [x] Initial model comparison, leakage-safe preprocessing, fixed split, and final held-out evaluation.
- [x] Eight-stage persisted workflow with independent reruns, logs, artifact integrity, and MLflow records.
- [x] Absolute and incumbent gates; bad-data and bad-model failures preserve production predictions/version.
- [x] Real MLflow model registration, aliases/lifecycle tags, and source/data/config/run lineage.
- [x] Container-ready API code, strict requests, Prometheus metrics, Grafana configuration, alert policies.
- [x] Three-batch monitoring report with actual labels and explicit alert evidence.
- [x] Executed model rollback and in-process HTTP operational measurements.
- [x] Tests, Dockerfile, Compose setup, PR/release workflows, documentation and demonstration plan.
- [x] Two-page design note and one-page reflection provided as PDFs.

## Required before claiming the entire assignment is complete

- [ ] Install/start Docker on an unrestricted local host; build the image and execute container serving.
- [ ] Confirm actual network endpoint latency, health, errors, and Grafana/Prometheus behavior under a documented request workload.
- [ ] Capture actual MLflow run-history/registry and dashboard screenshots. `registry.json` is real exported evidence, not a UI screenshot.
- [ ] Initialize the project under Swagata's GitHub account when Git access is available. Both team members must make genuine commits they understand.
- [ ] Create a legitimate passing PR and an intentional failing-check PR; fix the failure and retain real CI history. Do not invent screenshots or authorship.
- [ ] Merge to main and execute the image/release workflow. Configure the self-hosted deployment runner if demonstrating automated persistent deployment.
- [ ] Test the container/image rollback path on that host; model-pointer rollback has already passed locally.
- [ ] Perform a clean-environment/fresh-clone reproduction and compare validation MAE within the configured 1e-6 tolerance. Current local tests reproduce the baseline, but a fresh clone has not been executed.
- [ ] Record or present the 5–10 minute full-loop demonstration with both students explaining and modifying the work.

These are environmental/account/presentation requirements, not hidden completed steps. Git access remains deferred by the user's instruction. This agent's sandbox rejected local socket binding; Docker runtime is absent. The Python Docker SDK is not Docker Engine.
