# Free public API demo on Render

## Status (23 October 2026)

Live on Render Free (Singapore), deployed automatically from `main` by GitHub Actions.

- Dashboard: https://group4-mlflow-capstone.onrender.com/ · API docs: `/docs` · lineage: `/lineage`
- Service ID: `srv-dbch1h5g1s2s73bimspg`; native Render auto-deploy is off (`render.yaml`).
- Every merge to `main` runs *Build and release*; its `deploy-render` job deploys that exact commit and
  fails unless live `/lineage` reports it. The live commit is always visible on the dashboard.
- Rollback: *Roll back Render deployment* workflow (procedure in `OPERATIONS.md`, test in
  `reports/render_rollback.json`).
- Load test: `reports/load_test.json` (0 errors; p95 above 200 ms with 5 concurrent clients).

## What this deployment provides

A public HTTPS prediction API with `/docs`, `/health`, `/predict`, `/lineage`,
and `/metrics`. The updated Dockerfile builds the checked-out source with locked dependencies,
records RENDER_GIT_COMMIT in model lineage, runs the gated pipeline at build time,
and includes the resulting model state. The source-build update replaces the initial pinned-image demo. Confirm the
live /lineage source.commit matches the latest successful GitHub commit.
Restarts restore that image's model instead of requiring persistent storage.

This is a public demo of one release. It does not host the full Compose stack,
retain new MLflow history across restarts, or supply a persistent monitoring
server. Continue using Compose for the full monitoring and rollback demo.
The free service has 512 MB memory and one worker; see reports/load_test.json for measured latency under load.
It sleeps after 15 minutes without incoming traffic and can take time to wake.

## Account setup (already completed; recovery reference)

1. Create a Render account at https://dashboard.render.com/ using your GitHub account.
2. Use the Hobby workspace and Free service plan. Do not select a paid plan.
3. If Render requires a payment card for your account, stop: the user's constraint
   is no payment card. Account verification requirements cannot be bypassed.

## Initial service creation (already completed; do not create a duplicate)

1. New → Web Service → connect `Swagata-Bhowmik/group4-mlflow-capstone`.
2. Name: `group4-mlflow-capstone`; branch: `main`; runtime: Docker.
3. Leave the root directory at the repository root.
4. Dockerfile path: `deploy/render/Dockerfile`; Docker build context: `.`.
5. Instance type: Free. Health check path: `/health`.
6. No Docker Hub token is needed to pull the public image. No secrets are needed
   by this demo application.
7. Create the service; inspect build and runtime logs.
8. Record the assigned HTTPS URL. Verify `/health`, use `/docs` to submit a
   prediction, and inspect `/lineage` and `/metrics` before claiming deployment.

For agent-managed setup, create a Render API key privately and provide its local
credential-file path. Do not paste keys into chat or commit them. Account signup
and email verification must be completed by the account owner.

## Updating the model release

Store RENDER_API_KEY as a GitHub Actions repository secret and set repository
variable ENABLE_RENDER_DEPLOY=true. Keep Render native Auto-Deploy off to avoid
duplicate deployments. Push or merge to main: after the release job succeeds,
the deploy-render job sends that exact GITHUB_SHA to Render, waits for a live
deployment, and verifies the public health and model lineage. Failure is reported
in GitHub Actions. This works with the existing public repository URL.
Verify a real push and the new /lineage source commit before claiming automation.
Each image remains a fixed demo model;
runtime training and persistent lifecycle management belong to the Compose host.

## References

- https://render.com/docs/free
- https://render.com/docs/docker
- https://render.com/docs/web-services
- https://render.com/docs/compute-plans
