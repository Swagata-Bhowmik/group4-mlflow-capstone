# Free public API demo on Render

## Status

Deployment files prepared; no Render service created or live endpoint verified yet.
The Docker Hub release and GitHub release workflow have succeeded.

## What this deployment provides

A public HTTPS prediction API with `/docs`, `/health`, `/predict`, `/lineage`,
and `/metrics`. The Dockerfile pins the successful Docker Hub image by digest,
runs the gated pipeline at build time, and includes the resulting model state.
Restarts restore that image's model instead of requiring persistent storage.

This is a public demo of one release. It does not host the full Compose stack,
retain new MLflow history across restarts, or supply a persistent monitoring
server. Continue using Compose for the full monitoring and rollback demo.
The free service has 512 MB memory; actual memory fit remains to be verified.
It sleeps after 15 minutes without incoming traffic and can take time to wake.

## Account setup

1. Create a Render account at https://dashboard.render.com/ using your GitHub account.
2. Use the Hobby workspace and Free service plan. Do not select a paid plan.
3. If Render requires a payment card for your account, stop: the user's constraint
   is no payment card. Account verification requirements cannot be bypassed.

## Deploy after this Dockerfile is pushed to GitHub

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

Update the image digest and matching GITHUB_SHA in the Dockerfile together after
a new release passes CI. Rebuild on Render. Its image remains a fixed demo model;
runtime training and persistent lifecycle management belong to the Compose host.

## References

- https://render.com/docs/free
- https://render.com/docs/docker
- https://render.com/docs/web-services
- https://render.com/docs/compute-plans
