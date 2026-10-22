# Free public API demo on Render

## Status

Deployed successfully on Render Free in Singapore.

- API docs: https://group4-mlflow-capstone.onrender.com/docs
- Health: https://group4-mlflow-capstone.onrender.com/health
- Service ID: `srv-dbch1h5g1s2s73bimspg`
- Latest verified deployment ID: `dep-dbcnth2vcj2c73f9lt2g`
- Latest verified deployment commit: `b608040a3dd52dc2514ce018ab990ab7d443ff1a`
- Initial deployment: all five endpoint checks returned HTTP 200; prediction returned 97.8148 lakhs.
- Initial evidence: `reports/render_deployment.json`. Current automatic deployment evidence: `reports/render_auto_deployment.json`.
- Render native After CI Checks Pass did not trigger the source update.
- Direct GitHub Actions → Render API automation is enabled and verified.
  Commit b608040a3dd52dc2514ce018ab990ab7d443ff1a deployed automatically,
  and public lineage matches. See reports/render_auto_deployment.json.
The Docker Hub release and GitHub release workflow have succeeded.

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
The free service has 512 MB memory; startup and one prediction succeeded within this plan; sustained load is untested.
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
