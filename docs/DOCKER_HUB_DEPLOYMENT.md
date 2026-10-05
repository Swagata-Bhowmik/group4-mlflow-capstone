# Docker Hub → Windows or Linux server

**Chosen route:** GitHub stores code and runs tests. Docker Hub stores the built application image. Your Windows Docker Desktop or a Linux server runs the image together with MLflow and monitoring.

**Current status:** Configuration is prepared. No Docker Hub account, image upload, server or remote deployment has been created by the assistant. You must complete account sign-in and choose/provide the destination host. No paid service has been selected.

## 1. Create your Docker Hub account and repository

1. Open [Docker Hub](https://hub.docker.com/) and create/sign into your account.
2. Complete any email verification.
3. Note your **Docker username**. It may differ from your GitHub username.
4. Create a repository named **`group4-mlflow-capstone`** under that username.
5. Choose visibility deliberately: a public image makes its packaged source/data accessible; a private image requires authentication to pull. Check your account's current limits before choosing paid features.

The resulting image name will be:

```text
YOUR_DOCKER_USERNAME/group4-mlflow-capstone
```

You do not upload the ZIP through this page. The workflow builds the image and pushes it to the repository.

## 2. Give GitHub permission to publish images

1. In Docker account settings, create a **personal access token** for this project, with **Read and Write** permission. Delete permission is unnecessary.
2. In your GitHub project, open **Settings → Secrets and variables → Actions**.
3. Under **Variables**, create:

| Name | Value |
|---|---|
| `DOCKERHUB_USERNAME` | Your actual Docker username |
| `DOCKERHUB_REPOSITORY` | `group4-mlflow-capstone` (optional; this is the default) |

4. Under **Secrets**, create:

| Name | Value |
|---|---|
| `DOCKERHUB_TOKEN` | The token created in Docker account settings |

Never put the token in a code file, screenshot, terminal command argument, or this conversation. GitHub's own `GITHUB_TOKEN` continues to create the GitHub release; it does not authenticate to Docker Hub.

These settings are required before the main-branch release workflow can pass. Pull-request quality checks do not require Docker Hub credentials.

References: [Docker access tokens](https://docs.docker.com/security/access-tokens/) and [Docker's GitHub Actions examples](https://docs.docker.com/build/ci/github-actions/manage-tags-labels/).

## 3. Build and publish through GitHub

1. Follow the GitHub setup/PR steps in `WINDOWS_START_HERE.md`.
2. Merge a valid change into `main` after its checks pass.
3. Open **Actions → Build and release**. It should validate the Docker settings, run tests, smoke-check a container, build and push the image, then create a release.
4. Confirm the image tag is visible in Docker Hub.
5. Open the GitHub release notes and save both references:

```text
Tag:    YOUR_DOCKER_USERNAME/group4-mlflow-capstone:FULL_COMMIT_SHA
Digest: YOUR_DOCKER_USERNAME/group4-mlflow-capstone@sha256:ACTUAL_IMAGE_DIGEST
```

Use the **digest** when deploying a specific release. A tag is a readable label; a digest identifies the exact image bytes. The prepared automatic deployment job uses the digest produced by the publishing job.

Save screenshots of the successful workflow, Docker Hub image/tag, and release notes. Uploading an image is not evidence that a server has started it.

**Platform:** This workflow currently builds `linux/amd64`, suitable for ordinary Intel/AMD Linux hosts and compatible Docker Desktop setups. An ARM-only server needs an ARM build or supported emulation; multi-platform publishing has not been configured or verified. Do not assume the image runs on every processor.

## 4. Run the published image on Windows first

Keep Docker Desktop running in Linux-container mode. Open PowerShell in the project folder containing `compose.yaml` and `monitoring/`.

Replace the example username, digest and commit below with the real values from the release. Do not include literal angle brackets.

```powershell
$env:COMPOSE_PROJECT_NAME = "group4-capstone"
$env:CAPSTONE_IMAGE = "YOUR_DOCKER_USERNAME/group4-mlflow-capstone@sha256:ACTUAL_IMAGE_DIGEST"
$env:GITHUB_SHA = "FULL_COMMIT_SHA"
```

For a private image, authenticate interactively:

```powershell
docker login --username YOUR_DOCKER_USERNAME
```

Paste a token at the password prompt, not into the command. Read-only access is sufficient on a host that only downloads images. Public images can normally be pulled without signing in, subject to registry limits.

Pull, create the serving model, and start the services:

```powershell
docker compose pull api pipeline mlflow
docker compose --profile jobs run --rm -e GITHUB_SHA="$env:GITHUB_SHA" pipeline
docker compose up -d --wait api mlflow prometheus grafana
Invoke-RestMethod -Uri http://localhost:8000/health
```

**Why run the pipeline here?** The image contains application code and supplied data, but trained model files and the MLflow database are created in persistent named volumes. Docker Hub does not copy those volumes from another machine. The first pipeline run creates the model/registry state for this host. On later releases, it applies the quality gates against that host's existing model.

Use the `compose.yaml` and monitoring files from the **same source commit as the release**, so external configuration matches the image. Do not mix an old image with an unrelated new checkout.

## 5. Run on a separate Linux server

The host must have a working Docker Engine and Compose plugin, sufficient available resources for the service stack, and a compatible processor. No server or cloud account has been provisioned. Your assignment permits only free tools/free-tier resources; check any hosting limits before creating one.

Copy or clone the corresponding project source commit onto the server. You need at least the matching Compose file, monitoring directory, and deployment script in addition to image access.

In the server's Bash terminal, from that project folder:

```bash
export COMPOSE_PROJECT_NAME=group4-capstone
export CAPSTONE_IMAGE='YOUR_DOCKER_USERNAME/group4-mlflow-capstone@sha256:ACTUAL_IMAGE_DIGEST'
export GITHUB_SHA='FULL_COMMIT_SHA'
```

For a private image, run `docker login --username YOUR_DOCKER_USERNAME` and enter a read token at its prompt. Then:

```bash
bash scripts/deploy.sh
```

The script pulls the published image, runs the gated pipeline, starts the services and waits for health checks. A gate rejection leaves the previous API container alone. The prepared recovery branch attempts to restore the previous model/image if startup fails; that container-level recovery still needs actual host verification. First deployment has no earlier healthy release to restore.

### Access the server from your Windows browser

The supplied Compose file binds services to the server's **localhost**, not its public interface. For a private demonstration, keep those bindings and use SSH forwarding from Windows PowerShell:

```powershell
ssh -L 18000:127.0.0.1:8000 -L 5000:127.0.0.1:5000 -L 13000:127.0.0.1:3000 SERVER_USER@SERVER_ADDRESS
```

Keep that terminal open. Port 5000 must be free on Windows; if your local MLflow container is running, stop that local service first with `docker compose stop mlflow` from its project folder. Using local port 5000 keeps the forwarded browser host compatible with the configured MLflow allowed-host list. On Windows open:

- API: `http://localhost:18000/docs`
- MLflow: `http://localhost:5000`
- Grafana: `http://localhost:13000`

If you also want Prometheus, add `-L 19090:127.0.0.1:9090` to the SSH command before connecting.

A public HTTPS site would require a separate reverse-proxy, domain/network and authentication setup. The current project does not include that public-hosting configuration, and the professor's brief does not explicitly require a public URL.

## 6. Automatic deployment from GitHub

The release workflow already supports an optional `deploy` job:

1. Install/register a **Linux self-hosted runner** on the destination Docker host, following GitHub's instructions. On Windows use Ubuntu/WSL with Docker integration, as explained in `WINDOWS_START_HERE.md`.
2. Give the runner the extra label **`capstone`**.
3. Set GitHub repository variable **`ENABLE_LOCAL_DEPLOY=true`**. Despite the historical variable name, it can enable deployment to a remote self-hosted Linux runner too.
4. Keep exactly the intended deployment host available with that label; GitHub can choose any eligible runner if several share it.
5. Merge a valid change into `main`.

The release job publishes to Docker Hub. The deploy job logs into Docker Hub, consumes that release's **exact image digest**, and invokes `scripts/deploy.sh` with the real commit SHA and a fixed Compose project name. Without the variable/runner, publishing succeeds but persistent deployment is skipped.

## 7. State, updates and rollback

- `model-state` retains models, the MLflow database, and current/previous serving pointers.
- `report-data` retains generated reports.
- Moving the image does **not** migrate these volumes. This guide uses fresh pipeline execution on the new host. Moving an existing registry/history is a separate backup/restore task.
- Preserve the digest of the previous image and record model versions before changing a release.
- Use the tested model rollback command when appropriate: `docker compose --profile jobs run --rm pipeline python -m capstone rollback`.
- Restoring an earlier image requires setting `CAPSTONE_IMAGE` to the previous digest, pulling and restarting the services, then checking health, lineage and predictions. Coordinate model and application versions using `docs/OPERATIONS.md`.
- Do not delete volumes while collecting submission evidence.

## 8. What is complete versus still needed

**Prepared:** Docker Hub publishing workflow, credential-variable mapping, commit tags, digest handoff to deployment, Windows instructions, Linux server instructions, and matching archive.

**Not yet executed:** Account setup, authenticated image push, Docker build/run, server provisioning, network health check, live dashboard, actual GitHub release/deploy history. No hosting or subscription has been purchased.

**Your next action:** Create the Docker Hub account and the `group4-mlflow-capstone` repository. Keep the username handy. Configure the token directly in GitHub when your source repository is ready; do not send the token to the assistant.
