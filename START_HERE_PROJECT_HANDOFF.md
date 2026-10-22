# Group 4 — current project handoff

**Updated 22 October 2026.** For the complete portable AI context, read **[CLAUDE.md](CLAUDE.md)**. Give that file to Claude first; it explains the assignment, work completed, files, deployment, credentials, Git state, and remaining tasks.

## What was requested

An eight-stage house-price MLflow pipeline from raw data through validation, training, evaluation, registration, deployment, and monitoring, with safe failures, rollback, CI/CD, and presentation evidence.

Team: Swagata Bhowmik (B053), Sumit Kothari (B062). Professor: Dr. Santosh Kumar. Current computer: this Mac; the Windows plan is historical.

## What is ready

- 🟢 Pipeline, model comparison, final evaluation, MLflow registry and local rollback evidence.
- 🟢 Three-batch monitoring reports, tests, Docker/Compose configuration, design/reflection PDF drafts.
- 🟢 Public GitHub repository, Docker Hub images and GitHub releases.
- 🟢 Live API: https://group4-mlflow-capstone.onrender.com/docs
- 🟢 Automatic deployment verified: push to main → checks/release → Render → live health and commit verification.

Latest verified automatic deployment: **b608040**, workflow [39715048382](https://github.com/Swagata-Bhowmik/group4-mlflow-capstone/actions/runs/39715048382).

## What remains

- 🟡 Passing/failing PR evidence.
- 🟡 Full live MLflow/Grafana/Prometheus demonstration and screenshots.
- 🟡 Real network safe-failure, rollback, and workload measurements.
- 🟡 Explicit fresh-clone reproducibility record and final evidence packaging.
- 🟡 Updated PDFs/ZIP and team presentation.

The live Render Free service hosts the API demo. It sleeps when idle and has temporary runtime storage. The full persistent monitoring stack is separate. The assignment is not completely submission-ready yet.

## Important Git note

Before synchronization, local HEAD was `2be7c54`; remote main advanced through `b608040` and the documentation synchronization commit via GitHub API. Local files include newer work. Do not force-push, reset, or blindly pull over them. Follow the safe synchronization guidance in CLAUDE.md. This documentation refresh is included in the remote synchronization commit. Updating local Git metadata still requires the user's Terminal because the assistant cannot write `.git`.

## Read next

| File | Purpose |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Complete current AI handoff |
| [docs/SUBMISSION.md](docs/SUBMISSION.md) | Submission checklist |
| [docs/RENDER_DEPLOYMENT.md](docs/RENDER_DEPLOYMENT.md) | Live cloud service and auto-deployment |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Pipeline and Compose operations |
| [docs/DEMO.md](docs/DEMO.md) | Presentation flow |
| [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) | Current pointer and detailed historical research |

Earlier handoff preserved in [docs/history/HANDOFF_2026-10-05.md](docs/history/HANDOFF_2026-10-05.md); it is not the current status.
