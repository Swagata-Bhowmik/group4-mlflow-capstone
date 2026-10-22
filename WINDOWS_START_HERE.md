> **Current status: 22 October 2026.** Read [CLAUDE.md](CLAUDE.md) first. GitHub setup, Docker Hub publishing, Render API hosting, and automatic deployment are complete. This guide retains earlier setup/reference instructions; do not repeat completed steps. The current workstation is macOS.

# Windows execution guide — Group 4

**For:** Swagata Bhowmik (B053) and Sumit Kothari (B062)  
**Project:** Capstone: End-to-End MLflow Pipeline from Raw Data to Monitored Deployment  
**Last updated:** 5 October 2026  
**First read `START_HERE_PROJECT_HANDOFF.md` for the simple overall status and division of responsibilities.** Use this file afterward for detailed Windows commands and screenshots. Follow the steps in order; you do not need to understand every technical file before starting.

> **Current status in one sentence:** The program, local evidence, documents, and deployment files are built; the remaining work is to run the project on your Windows/Docker setup, obtain real GitHub and live-service evidence, and prepare the team presentation.
>
> **Important Windows detail:** Use **Docker Desktop with Linux containers**. The project uses `fcntl`, a Linux/macOS file-locking module. Do **not** follow the README's native Python/venv commands in ordinary Windows PowerShell. PowerShell will control Docker; Python will run inside the Linux container.

## 1. What your professor asked you to submit

The company in the assignment wants to predict property asking prices in **rupees lakhs**. A complete system must:

1. Read the supplied historical data.
2. Reject unacceptable data.
3. Prepare inputs and train a model.
4. Reject a model that is too inaccurate or worse than the existing model.
5. Record the model, its data, code, settings, and results in MLflow.
6. Serve predictions through a containerized API.
7. Monitor speed, errors, prediction values, and changes in the three later batches.
8. Keep the existing working model when an update fails.
9. Automatically test proposed GitHub changes and build/release on a main-branch update.
10. Demonstrate the complete process in 5–10 minutes, with both members participating.

Required hand-in: one repository with source/configuration/tests/workflows/Dockerfile/README; a design note of at most two pages; workflow graph; run-history and registry screenshots; two failure demonstrations; lineage evidence; genuine CI/release history; three-batch monitoring; a 5–10 minute demonstration; and a one-page reflection.

**The ZIP is a transfer package. It does not replace the required GitHub repository, real workflow history, or presentation.**

## Why Docker rather than only Streamlit?

This choice follows the assignment. Task 7 requires a **containerized API**. Task 6 requires building a **deployable image**, tagging it to link it to a commit, and demonstrating release/rollback behavior. A Streamlit interface alone does not demonstrate those requirements.

Docker is the packaging and execution environment, not necessarily paid internet hosting. For this assignment you can run the containers locally on Windows and show the API, registry and monitoring in your browser. A public URL is not explicitly required in the supplied brief. The GitHub release/persistent automated deployment demonstration is a separate requirement handled by the prepared workflow and local runner.

A Streamlit frontend could be added later to accept property details and call the API. That would be extra presentation work, not a replacement for the required containerized backend. The existing API already offers a browser form at `/docs`, so you can enter details and show predictions without building another interface. Replacing the container requirement entirely would need clarification/approval from the instructor; the current plan keeps the stated acceptance criteria.

## 2. Status key — what “ready” means here

| Label | Meaning |
|---|---|
| 🟢 READY / VERIFIED | File exists and its relevant local computation or document check was performed |
| 🟡 PREPARED / RUN ON WINDOWS | Implementation exists, but its container/network/GitHub execution is not yet proven |
| ⬜ YOUR REMAINING ACTION | Requires your computer, account, screenshot, or presentation |

The assistant's environment did not have Docker Engine and blocked opening a server port. GitHub access was deferred. Therefore **no real GitHub PRs/releases, Docker deployment, or live dashboard screenshots have been produced**. We have not claimed otherwise.

## 3. What has already been done

- Read the entire professor's brief and recorded the requirements.
- Preserved the supplied CSVs and checked their SHA-256 fingerprints.
- Confirmed 4,000 historical records and three incoming batches of 500 each.
- Checked missing values, duplicates, allowed categories, numeric ranges, and batch differences.
- Compared a constant-price predictor, Ridge, random forest, and gradient boosting.
- Selected Ridge using validation error; kept training and validation preprocessing separate.
- Evaluated the final 800-row historical test once, after selection.
- Built all eight stages with individual reruns, saved outputs, logs, and artifact-integrity checks.
- Installed and used real MLflow for tracking and registered model versions.
- Executed bad-data and bad-model failures while keeping the previous model and response unchanged.
- Executed and verified model rollback from release 2 to release 1.
- Evaluated all three incoming batches and produced a colored monitoring report.
- Tested the API through in-process HTTP, including invalid input and metrics.
- Passed **15 automated tests**.
- Reproduced validation MAE exactly from a fresh directory using the existing dependencies.
- Wrote Docker/Compose, Prometheus/Grafana, GitHub checks/release files and operations instructions.
- Created and visually inspected a **two-page design PDF** and **one-page reflection PDF**.

### Actual results — use these numbers, not invented ones

| Result | Value / meaning |
|---|---|
| Constant-price validation MAE | ₹17.73 lakhs |
| Ridge validation MAE | ₹5.742 lakhs; about 67.6% lower than the constant baseline |
| Final historical test MAE | ₹5.775 lakhs over 800 reserved records |
| Final historical test RMSE | ₹7.506 lakhs |
| Batch 1 MAE | ₹5.562 lakhs; no configured alert |
| Batch 2 MAE | ₹6.867 lakhs; property-area input shift; no configured MAE alert |
| Batch 3 MAE | ₹13.113 lakhs; input shifts and accuracy alert |
| Local safety tests | Bad data and poor model rejected; same production response preserved |
| Local benchmark | 100 warm in-process HTTP requests, zero errors, p95 about 3.69 ms |

**MAE** means average absolute error. ₹5.775 lakhs does not mean every prediction is within that amount. **RMSE** gives more weight to large mistakes. The local benchmark is **not** a Windows/network load-test result.

## 4. Ready files — documents and submission material

All paths below are relative to the extracted project folder. A folder is just an organizer; keep the structure unchanged.

| File | What it contains | Status / what you do |
|---|---|---|
| `group4_capstone_submission.zip` | Transfer package containing code, original data, reports and documents | 🟢 Download the newest version and extract it; ZIP is not inside itself |
| `WINDOWS_START_HERE.md` | This inventory and Windows step-by-step guide | 🟢 Your main checklist |
| `README.md` | Main project explanation, architecture diagram, results and commands | 🟢 Include in repository; use this Windows guide for Windows commands |
| `PROJECT_CONTEXT.md` | Full requirements, decisions, work history, measured evidence and limitations | 🟢 Give this to an AI session to resume work |
| `output/pdf/design_note.pdf` | Business objective, architecture, thresholds, safety, monitoring and limitations | 🟢 Two pages, ready as a draft deliverable; update stated environment limitations after completing Windows evidence |
| `output/pdf/reflection.pdf` | What worked, limitations, and future improvements | 🟢 One page; both members must read and personalize/review before submission |
| `docs/DEMO.md` | Eight-minute presentation outline and questions to practice | 🟢 Guide ready; recording/presentation still needed |
| `docs/DOCKER_HUB_DEPLOYMENT.md` | Docker Hub account, image publishing and Windows/Linux host deployment | 🟡 Prepared; account and host execution pending |
| `docs/OPERATIONS.md` | Stage inputs/outputs, alerts, rollback and recovery | 🟢 Instructions ready; container/image recovery still needs execution |
| `docs/SUBMISSION.md` | Completed and pending acceptance checklist | 🟢 Update only when remaining steps really pass |
| `Capstone End_to_End_Pipeline.docx` | Original professor's assignment | 🟢 Reference; not a report we wrote |

## 5. Ready files — measured evidence

| File | Contents | Important distinction |
|---|---|---|
| `reports/monitoring.html` | Colored, human-readable report for all three incoming batches | Open by double-clicking; reflects actual measured local results |
| `reports/monitoring.json` | Exact drift statistics, error values and alerts for each batch | Machine-readable evidence behind the HTML |
| `reports/final_test.json` | Final historical test error and sample count | Already evaluated once; do not repeatedly tune against it |
| `reports/safe_failures.json` | Before/after responses for rejected data and model updates | Verified using in-process HTTP; collect live Windows evidence too |
| `reports/rollback.json` | Successful model-version rollback evidence | Model-pointer rollback; not a verified container-image rollback |
| `reports/lineage.json` | Model-to-run-to-data/code/configuration trace | Real historical local evidence; absolute Mac paths are not Windows launch paths |
| `reports/registry.json` | Actual MLflow run statuses and model versions | An exported record, **not** an MLflow UI screenshot |
| `reports/operational.json` | Local request count, errors, timings and measurement method | In-process benchmark, not live network performance |
| `reports/prometheus_metrics.txt` | Captured metrics response from the API | Actual local response; live Grafana capture pending |
| `reports/source_integrity.json` | Confirms original CSV fingerprints did not change | Include as data-integrity evidence |
| `reports/reproduction.json` | Same validation MAE from a fresh directory | Same installed dependencies; not a clean Windows build/fresh Git clone |
| `reports/pytest.log` | Human-readable test result: 15 passed | Genuine local test output |
| `reports/junit.xml` | Test results in standard machine-readable format | Useful for automated checks |
| `reports/demo.log` | Detailed local pipeline, failure and rollback output | Reference evidence |
| `reports/final_test.log` | Console output of the final test evaluation | Reference evidence |
| `reports/monitoring_run.log` | Console output of monitoring | Reference evidence |
| `reports/reproduction.log` | Console output of the fresh-directory check | Reference evidence |

Keep the provided `reports/` as historical evidence. Save your new Windows captures under `windows-evidence/` so results from different environments are not confused.

## 6. Ready files — the program and configuration

You do not have to open every code file now. This table explains what each does.

| File | Purpose | Status |
|---|---|---|
| `config.yaml` | Main settings: paths, features, thresholds, model, monitoring and API | 🟢 Validated in local runs |
| `capstone/config.py` | Rejects invalid settings | 🟢 Tested |
| `capstone/core.py` | Eight-stage workflow, MLflow, gates, deployment and rollback | 🟢 Tested locally; Docker execution pending |
| `capstone/api.py` | Accepts property details and returns prices; exposes health/lineage/metrics | 🟢 In-process tested; network execution pending |
| `capstone/monitoring.py` | Compares batches, measures error, writes monitoring reports | 🟢 Executed |
| `capstone/demo.py` | Runs failure, rollback and API evidence demonstrations | 🟢 Executed locally |
| `capstone/__main__.py` | Makes `python -m capstone ...` commands work | 🟢 Executed |
| `capstone/__init__.py` | Marks the folder as a Python package | 🟢 Ready |
| `tests/test_capstone.py` | Fifteen tests for config, data, leakage, reruns, integrity and safety | 🟢 Passed locally |
| `requirements.txt` | Direct Python dependencies | 🟢 Written |
| `requirements.lock` | Exact installed dependency versions and their dependencies | 🟡 Clean installation/build needs verification |
| `data_manifest.json` | Original dataset fingerprints for reproducibility | 🟢 Ready |
| `capstone_house_prices_train.csv` | Supplied 4,000 historical labeled listings | 🟢 Unchanged |
| `capstone_incoming_batches.csv` | Supplied 1,500 labeled later listings | 🟢 Unchanged |
| `.gitignore` | Prevents runtime state, environments and temporary files entering Git | 🟢 Ready; Git history not created |
| `.dockerignore` | Excludes unnecessary/sensitive local files from image builds | 🟢 Ready |

### Earlier model-comparison files

| File | Contents |
|---|---|
| `experiments/baseline_config.yaml` | Settings for the earlier four-model comparison |
| `experiments/run_baselines.py` | Script used for that comparison |
| `experiments/baseline_results/results.json` | Exact comparison metrics and package versions |
| `experiments/baseline_results/split_membership.csv` | Which listing IDs belong to training, validation and reserved test |
| `experiments/baseline_results/validation_predictions.csv` | Actual validation prices and four models' predictions |

The locally saved `experiments/baseline_results/selected_model.joblib` is **intentionally excluded from the transfer ZIP**. Training recreates the model. Neither `.venv/` nor `state/` is transferred: they contain machine-specific dependencies and runtime state. Docker will recreate them appropriately on Windows.

## 7. Prepared infrastructure files — not yet execution evidence

| File | What it will do when run |
|---|---|
| `Dockerfile` | Builds the Linux image containing the Python application |
| `compose.yaml` | Connects the pipeline job, prediction API, MLflow, Prometheus and Grafana |
| `.github/workflows/ci.yml` | Tests pull requests and runs a lightweight pipeline |
| `.github/workflows/release.yml` | Tests/builds/publishes a commit-tagged image and release on main; can deploy through a configured self-hosted runner |
| `monitoring/prometheus.yml` | Tells Prometheus where to collect API metrics |
| `monitoring/alerts.yml` | Generated alert conditions for latency, errors, freshness and availability |
| `monitoring/dashboard.json` | Grafana dashboard panels |
| `monitoring/grafana/provisioning/datasources/prometheus.yml` | Connects Grafana to Prometheus |
| `monitoring/grafana/provisioning/dashboards/default.yml` | Loads the dashboard automatically |
| `scripts/generate_monitoring_config.py` | Regenerates alert/dashboard files from the main YAML settings |
| `scripts/snapshot_registry.py` | Exports actual MLflow run/version records |
| `scripts/check_reproduction.py` | Repeats the validation run from a fresh directory |
| `scripts/deploy.sh` | Bash script for container rollout and health-failure rollback; use Linux/WSL, not native PowerShell |
| `scripts/build_documents.py` | Recreates the PDFs with ReportLab; optional document tooling, separate from application dependencies |

## 8. What you need on Windows

### Needed first

- A supported Windows computer and permission to enable virtualization/WSL if necessary.
- Internet access for Docker and dependency/image downloads.
- Docker Desktop running **Linux containers**; WSL 2 is the recommended route for this project.
- The latest project ZIP, extracted completely.
- A browser such as Edge or Chrome and PowerShell.

### Needed later

- Your GitHub account; Sumit's own GitHub account for genuine contributions.
- GitHub Desktop for a simpler graphical Git workflow.
- A screenshot tool (Windows Snipping Tool is sufficient).
- A screen recorder and microphone for the final demonstration.
- WSL/Ubuntu terminal for the optional self-hosted **Linux** deployment runner, needed to demonstrate the prepared persistent automatic deployment job.

No AWS account, paid cloud server, GPU, native Anaconda install, or separate native Python install is needed for the Docker-first steps below. Check current Docker requirements and your own machine before installation: [Docker's Windows installation page](https://docs.docker.com/desktop/setup/install/windows-install/).

## 9. Windows steps — follow in this order

### Step 1 — Download and extract

1. Download the **updated** `group4_capstone_submission.zip` from this conversation.
2. Right-click it → **Extract All**.
3. Put the extracted `group4-capstone` folder somewhere simple, for example `C:\Projects\group4-capstone`.
4. Open that folder. You should see `Dockerfile`, `compose.yaml`, `config.yaml`, `README.md`, and this guide together.
5. Double-click `reports\monitoring.html` and open the two PDFs in `output\pdf` to see what is already ready.

**Success:** You can see the project files, monitoring report and both PDFs. Do not run commands inside the ZIP itself.

### Step 2 — Install/start WSL and Docker Desktop

1. Download Docker Desktop from its [official Windows installation page](https://docs.docker.com/desktop/setup/install/windows-install/). Select the installer matching your computer's processor; most Windows laptops use x86_64, but check Windows Settings → System → About.
2. Follow the installer, choosing the WSL 2 backend when offered.
3. If WSL is missing, open **PowerShell as Administrator**, run the command below, then restart Windows if requested:

```powershell
wsl --install
```

4. Open Ubuntu once if prompted and complete its first-run account setup. This is a local Linux account, not your GitHub login.
5. Open Docker Desktop and wait until it says the engine is running. Use **Linux containers**.
6. Open an ordinary PowerShell window and check:

```powershell
wsl --version
docker version
docker compose version
```

**Success:** Docker reports a working client **and server**, and Compose prints a version. If only the client appears or you see a daemon-connection error, Docker Desktop is not ready. If installation requires virtualization changes, follow the machine manufacturer's/Docker's instructions rather than changing unrelated settings.

Official WSL instructions: [Microsoft: Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install). Docker's [WSL backend guide](https://docs.docker.com/desktop/features/wsl/) explains the integration.

### Step 3 — Open PowerShell in the project folder

In File Explorer, open the extracted project folder, click the address bar, type `powershell`, and press Enter. Alternatively:

```powershell
Set-Location "C:\Projects\group4-capstone"
Get-ChildItem
$env:COMPOSE_PROJECT_NAME = "group4-capstone"
New-Item -ItemType Directory -Force windows-evidence
```

Replace the path only if you extracted elsewhere. Set `COMPOSE_PROJECT_NAME` again whenever you open a new PowerShell window; it keeps the same container/volume names across folders and terminals.

**Success:** The listing includes `compose.yaml`. Keep this terminal open for the following steps.

### Step 4 — Build the application and run tests

Run commands one at a time:

```powershell
docker compose config
docker compose build
```

The first image build downloads dependencies and may take a while. **Do not continue if the build ends with an error.** Save the error text so it can be diagnosed; do not randomly change package versions.

Then:

```powershell
docker compose --profile jobs run --rm pipeline python -m pytest -q --junitxml=reports/windows_junit.xml 2>&1 | Tee-Object -FilePath windows-evidence\tests.txt
```

**Success:** All 15 tests pass. These tests use temporary model state and do not establish the main serving model. Save a screenshot as `01_windows_tests.png`.

**Important:** Container installation has not previously run on Windows. These are the intended verification steps, not a claim that your first build cannot encounter a compatibility issue.

### Step 5 — Train and register the real serving model

```powershell
docker compose --profile jobs run --rm pipeline 2>&1 | Tee-Object -FilePath windows-evidence\pipeline.txt
```

**Success:** You see successful stages from `ingest` through `monitor`, plus `RUN_DIRECTORY=...`. MLflow and trained model state are now in Docker's named `model-state` volume. Reports are in `report-data`. They are **not automatically written into the Windows `reports` folder**.

If a gate fails unexpectedly, save the output and diagnose it. Do not loosen thresholds solely to force a pass.

### Step 6 — Start the live services

```powershell
docker compose up -d --wait api mlflow prometheus grafana
docker compose ps
```

Open these pages in your browser:

| Address | What you should see |
|---|---|
| `http://localhost:8000/docs` | Interactive prediction API page |
| `http://localhost:8000/health` | Healthy response with model version |
| `http://localhost:8000/lineage` | Model, run, data, source and settings |
| `http://localhost:5000` | MLflow runs and registered models |
| `http://localhost:9090/targets` | Prometheus target; API should be UP |
| `http://localhost:3000` | Grafana; open the Group 4 dashboard |

**Success:** Pages load and the API is healthy. Save screenshots `02_live_api.png`, `03_mlflow_runs.png`, `04_model_registry.png`, and `05_lineage.png`.

### Step 7 — Make a real prediction

On `http://localhost:8000/docs`, expand **POST /predict**, click **Try it out**, paste this JSON, and click **Execute**:

```json
{
  "records": [
    {
      "Area_sqft": 1200,
      "Bedrooms": 2,
      "Bathrooms": 2,
      "Age_Years": 10,
      "Distance_to_Center_km": 8,
      "Neighborhood_Score": 7,
      "Has_Parking": 1,
      "Property_Condition": "Good",
      "City_Zone": "Central"
    }
  ]
}
```

**Success:** HTTP 200 with `model_version` and `price_lakhs`. Record the actual value you receive; do not invent an expected price. Save `06_prediction.png`.

For the next steps, also define the same request in PowerShell:

```powershell
$body = @'
{"records":[{"Area_sqft":1200,"Bedrooms":2,"Bathrooms":2,"Age_Years":10,"Distance_to_Center_km":8,"Neighborhood_Score":7,"Has_Parking":1,"Property_Condition":"Good","City_Zone":"Central"}]}
'@
Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -ContentType application/json -Body $body
```

### Step 8 — Demonstrate rejected updates and model rollback

First run the built-in demonstration **inside Docker**:

```powershell
docker compose --profile jobs run --rm pipeline python -m capstone demo 2>&1 | Tee-Object -FilePath windows-evidence\demo.txt
```

It creates separate deliberately bad demo inputs, rejects them, creates another valid release, and restores the earlier model. It does not change the original supplied CSVs. Its internal HTTP checks remain in-process even when run in Docker.

To also prove the live API survives a rejected update, use the request from Step 7:

```powershell
$before = Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -ContentType application/json -Body $body
$before | ConvertTo-Json -Depth 5 | Set-Content windows-evidence\before_bad_data.json

docker compose --profile jobs run --rm pipeline python -m capstone run --input state/demo_inputs/bad_missingness.csv 2>&1 | Tee-Object -FilePath windows-evidence\bad_data_rejection.txt

$after = Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -ContentType application/json -Body $body
$after | ConvertTo-Json -Depth 5 | Set-Content windows-evidence\after_bad_data.json
$before
$after
```

**Expected:** The pipeline command exits with an error explaining excessive missingness; that rejection is intentional. The live API still returns HTTP 200 with the **same model version and price**.

Repeat for the model-quality failure:

```powershell
$before | ConvertTo-Json -Depth 5 | Set-Content windows-evidence\before_bad_model.json
docker compose --profile jobs run --rm pipeline python -m capstone --config state/demo_inputs/bad_model.yaml run 2>&1 | Tee-Object -FilePath windows-evidence\bad_model_rejection.txt
$after = Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -ContentType application/json -Body $body
$after | ConvertTo-Json -Depth 5 | Set-Content windows-evidence\after_bad_model.json
```

**Expected:** The intentionally poor model is rejected; the live API response stays the same. Save `07_bad_data_safe.png` and `08_bad_model_safe.png` showing the failure and surviving endpoint response.

For an explicit live model rollback demonstration:

1. Save the current `/health` and `/predict` responses.
2. Run `docker compose --profile jobs run --rm pipeline` to create a second accepted release.
3. Verify `/health` now shows a new version.
4. Run the command below and verify the original version and prediction return:

```powershell
docker compose --profile jobs run --rm pipeline python -m capstone rollback 2>&1 | Tee-Object -FilePath windows-evidence\model_rollback.txt
Invoke-RestMethod -Uri http://localhost:8000/health
Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -ContentType application/json -Body $body
```

Save `09_model_rollback.png`. This proves rollback of the model inside a running container. Image/application-code rollback is a separate later check.

### Step 9 — Generate live traffic and capture the dashboard

The dashboard needs requests before charts show meaningful activity. With the same `$body` from Step 7:

```powershell
$times = [System.Collections.Generic.List[double]]::new()
$errors = 0
for ($i = 0; $i -lt 300; $i++) {
    $watch = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $null = Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -ContentType application/json -Body $body
    } catch {
        $errors++
    }
    $watch.Stop()
    $times.Add($watch.Elapsed.TotalSeconds)
    Start-Sleep -Milliseconds 200
}
$sorted = @($times | Sort-Object)
$result = [pscustomobject]@{
    method = "Windows PowerShell; live localhost HTTP; 300 sequential requests with 200ms gaps"
    requests = 300
    errors = $errors
    error_rate = $errors / 300.0
    p95_seconds = $sorted[[int][Math]::Ceiling($sorted.Count * 0.95) - 1]
}
$result | ConvertTo-Json | Set-Content windows-evidence\network_benchmark.json
$result
```

Record the measured result, even if a target is missed. This is a modest sequential local test, not a production capacity test. Return to Grafana, use the last 15 minutes and refresh. Save `10_grafana.png` and `11_prometheus_target.png`. Verify latency, request rate, errors and prediction distribution. Do not expect the error panel to be zero immediately after deliberately invalid requests.

### Step 10 — Export your fresh Windows reports

Refresh batch monitoring and registry evidence:

```powershell
docker compose --profile jobs run --rm pipeline python -m capstone monitor
docker compose --profile jobs run --rm -e PYTHONPATH=/app pipeline python scripts/snapshot_registry.py
```

Create a temporary stopped container from which to copy the reports:

```powershell
docker compose --profile jobs run --name group4-export pipeline python -c "print('Reports ready to copy')"
New-Item -ItemType Directory -Force windows-evidence\container-reports
docker cp group4-export:/app/reports/. .\windows-evidence\container-reports
docker rm group4-export
```

The last command removes only the temporary export container. Do **not** use `docker compose down -v`; that would delete your model/report volumes.

Open `windows-evidence\container-reports\monitoring.html` and save `12_batch_monitoring.png`. The transferred `final_test.json` may be the original historical final-test result already included in the image; do not label it as a new Windows evaluation. Windows tests and the reproduction report establish the repeated validation result. Do not delete the original final-test record just to rerun selection.

**Success:** Your screenshots, console logs, live network benchmark and newly exported reports are all in `windows-evidence/`.

### Step 11 — Put the project on Swagata's GitHub account

This starts the GitHub work that was previously deferred. Nothing has been uploaded for you.

1. Install GitHub Desktop from [desktop.github.com](https://desktop.github.com/) and sign into **Swagata's** account through its normal browser login.
2. Add the extracted project folder using **File → Add local repository**. It currently has no Git repository; if prompted, choose the option to create a repository in this folder. Check that it uses the existing folder, not a new empty nested folder.
3. Review the file list. Keep code, config, original CSVs, documentation, tests, workflows and selected evidence. Do not add virtual environments, tokens or runtime databases. The provided `.gitignore` excludes these.
4. Create the initial commit with an accurate message such as `Add capstone implementation and local evidence`.
5. Use **Publish repository**, choose Swagata's personal account, and name it, for example, `group4-mlflow-capstone`. Select visibility according to your professor's access requirement and your account's free usage limits. If private, grant the professor access when submitting.
6. On GitHub, invite `sum1tk` as a collaborator. Sumit must accept using his account.
7. Both members should make real changes they understand using their own accounts, for example correcting their explanation of a stage or documenting measured Windows evidence. Do not create fake commit identities or pretend assistant-produced work was individually authored.

Official instructions: [adding a local repository to GitHub Desktop](https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-a-repository-from-your-local-computer-to-github-desktop), [publishing with GitHub Desktop](https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-an-existing-project-to-github-using-github-desktop?platform=windows).

### Step 12 — Obtain real passing and failing PR evidence

A **pull request (PR)** is a proposed change that GitHub checks before it is merged into `main`.

**Passing PR:**

1. In GitHub Desktop, create a new branch such as `docs/windows-evidence`.
2. Make a genuine documentation improvement, such as adding your measured Windows setup/results.
3. Commit, publish the branch, and open a pull request into `main`.
4. Wait for **Quality checks** to finish. Save the passing checks screen as `13_passing_pr.png` and keep the URL.
5. Merge after checking the results. A merge to `main` triggers the release workflow.

**Intentional failing PR:**

1. Create a separate branch `demo/expected-check-failure`.
2. Add `tests/test_expected_ci_failure.py` containing:

```python
def test_deliberate_ci_failure():
    assert False, "Intentional capstone demonstration: CI must reject this change"
```

3. Commit it with a message clearly identifying the intentional failure, publish and open a PR.
4. Wait for the tests to fail. Save `14_failing_pr.png` and the URL.
5. **Do not merge the failing change.** Remove the deliberate test file on that branch and commit the correction.
6. Confirm the checks now pass; retain the history showing both failure and correction. If the PR has no remaining diff, close it; do not force a meaningless merge.

A failed PR test demonstrates CI protection. It is different from the runtime bad-data and bad-model gate demonstrations in Step 8; both kinds of evidence are needed.

### Step 13 — Publish to Docker Hub and obtain a real release

First complete account/repository/token setup in [docs/DOCKER_HUB_DEPLOYMENT.md](docs/DOCKER_HUB_DEPLOYMENT.md). GitHub variables: `DOCKERHUB_USERNAME`, optional `DOCKERHUB_REPOSITORY`; secret: `DOCKERHUB_TOKEN`. Docker Hub and GitHub usernames may differ. Never put the token in the project files.

1. After a valid merge into `main`, open **Actions → Build and release**.
2. Wait for tests, container smoke check, image push and release creation.
3. If an action fails, inspect the first failed step and fix the cause; do not claim success from merely seeing a workflow file.
4. Save `15_release_workflow.png`, the release URL, and the actual image tag shown in release notes.
5. Record the full commit SHA. The tag should look like `YOUR_DOCKERHUB_USERNAME/group4-mlflow-capstone:ACTUAL_COMMIT_SHA` if you chose that repository name.

The workflow uses `DOCKERHUB_TOKEN` for image publishing and GitHub's provided `GITHUB_TOKEN` for the GitHub release. Store the Docker token as a GitHub Actions secret only. Check Docker Hub and GitHub account allowances before relying on free usage. The release notes include an image digest: use that exact reference for deployment. Publishing an image is **not yet** proof that your persistent Windows endpoint was automatically updated.

### Step 14 — Complete persistent automatic deployment (Linux runner inside Windows)

This is the more technical remaining step. The existing workflow expects a **Linux** self-hosted runner labeled `capstone`, so use Ubuntu under WSL, not the native Windows runner download.

1. In Docker Desktop, enable WSL integration for Ubuntu. Open Ubuntu and verify `docker version` and `docker compose version` there.
2. On GitHub, open your repository's **Settings → Actions → Runners → New self-hosted runner**.
3. Choose **Linux** and the correct CPU architecture. Follow the exact download/configuration commands GitHub displays, in the Ubuntu terminal. GitHub gives a temporary registration token: use it only for setup and never commit or share it.
4. When asked for additional runner labels, add **`capstone`**. Keep the default labels too.
5. Before starting the runner, in that same Ubuntu terminal run:

```bash
export COMPOSE_PROJECT_NAME=group4-capstone
./run.sh
```

6. Leave the runner and Docker Desktop running while the workflow executes. The runner should appear **Idle** on GitHub when ready.
7. Under **Settings → Secrets and variables → Actions → Variables**, add repository variable **`ENABLE_LOCAL_DEPLOY`** with value **`true`**.
8. Make a genuine small change through a passing PR and merge it. A new main commit gives a new release tag; avoid repeatedly attempting to create an already-existing release tag.
9. Verify the workflow's **deploy** job succeeds and your live `/health` and `/lineage` show the new model/run and real commit SHA.
10. Save `16_automatic_deployment.png` and `17_commit_lineage.png`.

If GitHub's runner setup reports a missing Linux package, follow its setup diagnostics. Restrict who can push/trigger this runner; it executes repository deployment code on your computer. Official reference: [GitHub self-hosted runner management](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners?platform=linux).

**Stop condition for this step:** A green image-build/release job with the deploy job skipped is not a completed persistent deployment demonstration.

### Step 15 — Verify image rollback and fresh-clone reproduction

**Image/application rollback:**

The model rollback is already covered in Step 8. To verify the container release as well, retain two successful release image tags and the model versions associated with them. Use `docs/OPERATIONS.md` for the rollback procedure. From PowerShell, an explicit previous-image restart takes this form:

```powershell
$env:CAPSTONE_IMAGE = "YOUR_DOCKERHUB_USERNAME/group4-mlflow-capstone:PREVIOUS_REAL_COMMIT_SHA"
docker compose pull api mlflow
docker compose up -d --wait api mlflow
Invoke-RestMethod -Uri http://localhost:8000/health
docker inspect --format '{{.Config.Image}}' (docker compose ps -q api)
```

Replace the repository/tag with the **actual** previous successful release. If model rollback is also needed, use the pipeline rollback command before verifying predictions, following the recorded current/previous model versions. Do not toggle rollback blindly. Save before/after image tags, health and predictions as `18_image_rollback.png`. Restore the intended final release afterward. Testing a manual prior-image restore does not by itself prove the script's automatic health-failure recovery path; label which procedure you actually exercised.

**Fresh clone:**

1. Use GitHub Desktop to clone the repository into a different folder.
2. Open PowerShell there and use an isolated Compose project name:

```powershell
$env:COMPOSE_PROJECT_NAME = "group4-reproduction"
Remove-Item Env:CAPSTONE_IMAGE -ErrorAction SilentlyContinue
docker compose build --no-cache
docker compose --profile jobs run --rm pipeline python -m capstone run --stop-after evaluate
```

3. Compare validation MAE with **5.741987567526319** using tolerance **0.000001**. Save actual output as `19_fresh_clone.txt`.
4. This separate project has separate volumes. Do not start its API on port 8000 while the original API is running; reproduction through evaluation does not require a second server.
5. Return to the main project folder and set `$env:COMPOSE_PROJECT_NAME = "group4-capstone"` again before normal operation.

### Step 16 — Finalize documents and record the presentation

1. Review `docs/DEMO.md` together.
2. Both students should be able to explain preprocessing, model selection, gates, MLflow lineage, monitoring, and rollback, and make a small live modification.
3. Review/personalize the reflection. It is currently a technical draft; do not present it as personal learning neither member understands.
4. Update documentation status after Windows/GitHub evidence exists. The PDFs currently truthfully say Docker/GitHub/live evidence was pending; revise that text and regenerate the PDFs before final hand-in. Keep the design note at two pages and reflection at one page. Ask the assistant to update the document sources with your actual new results rather than editing PDF text blindly.
5. Record or present the 5–10 minute sequence: objective → code change/CI → pipeline → deployment → monitoring → safe failure. Both members explain a part and are prepared to answer questions about all parts.
6. Save the video as `Group4_Capstone_Demo.mp4`, or provide the professor-approved recording link/live demonstration format.

**Evidence still needs your participation:** A written demo script is not the actual team demonstration.

## 10. Exact final submission checklist

Create a final hand-in folder, for example `Group4_Final_Submission`, containing or linking to:

| Deliverable | File/link to hand in | What must be true |
|---|---|---|
| Repository | Actual GitHub repository URL | Contains code, config, tests, workflows, Dockerfile, data/version records and README; professor can access it |
| Design note | Updated `design_note.pdf` | At most two pages; reflects what actually ran |
| Reflection | Reviewed `reflection.pdf` | One page; both students understand it |
| Workflow graph | README diagram and design-note diagram | Matches the implementation |
| Run history and registry | `03_mlflow_runs.png`, `04_model_registry.png` | Screenshots from the real Windows/Docker run |
| Lineage | `05_lineage.png`, `17_commit_lineage.png`, exported JSON | Real model → run → data/config/code linkage, including actual commit after Git setup |
| Gate failures | `07_bad_data_safe.png`, `08_bad_model_safe.png`, JSON/logs | Rejection shown with continued serving and unchanged model |
| Rollback | `09_model_rollback.png`, `18_image_rollback.png`, logs | Exact tested procedures identified |
| CI/release | PR URLs, `13_passing_pr.png`, `14_failing_pr.png`, `15_release_workflow.png`, release URL | Genuine execution history |
| Deployment | `16_automatic_deployment.png`, live health output | Persistent deployment executed; not merely an image published |
| Monitoring | Latest `monitoring.html`/JSON, `10_grafana.png`, network benchmark | All three batches plus operational behavior explained |
| Reproduction | `19_fresh_clone.txt`, test results | Fresh clone reproduces metrics within stated tolerance |
| Demo | `Group4_Capstone_Demo.mp4` or approved presentation/link | 5–10 minutes, both members participate |
| Backup package | Updated project ZIP | Matches the final repository/documents; no secrets or local environments |

Use the professor's actual submission portal/format if it differs; no deadline or portal was supplied in the brief we received.

## 11. If something goes wrong

| Message/problem | What to do first |
|---|---|
| `docker` is not recognized | Finish Docker Desktop installation and reopen PowerShell |
| Cannot connect to Docker daemon | Open Docker Desktop and wait for its engine |
| `No module named fcntl` | You ran native Windows Python; use the Docker commands in this guide |
| Cannot find `compose.yaml` | Move into the extracted project root |
| Build/download failure | Save the first error; check network/package compatibility before changing dependencies |
| `/health` returns no model | Run Step 5 successfully before starting/using the API; check pipeline logs |
| Page cannot be reached | Run `docker compose ps`, then `docker compose logs --tail 80 api` |
| Blank Grafana panels | Send requests, check Prometheus target UP, use a recent time range, refresh |
| Export container name exists | If it is your old stopped helper, remove it with `docker rm group4-export`, then repeat export |
| Final evaluation already recorded | Expected: the original final result is preserved; do not delete it to tune repeatedly |
| Deploy job skipped | The Linux runner/label and `ENABLE_LOCAL_DEPLOY` setup are not complete |
| Release tag already exists | Use a new genuine main-branch commit instead of rerunning duplicate release creation |

When requesting help, provide the step number and the first relevant error text. Never share passwords or access tokens.

## 12. What you personally do versus what is already written

**You personally need to:** install/open Docker, run the guided commands, sign into GitHub, complete account authorization, capture real screenshots, make genuine contributions, and rehearse/present.

**You do not need to rewrite:** the model, pipeline, API, tests, monitoring calculations, Docker setup or GitHub workflow files. They are included, subject to fixing any issue exposed by the remaining Windows/container execution.

**Your immediate next step is Step 1, then Step 2.** Complete those before thinking about GitHub or presentation recording.
