# Mac Terminal — ordered commits using the two identity wrappers

**Repository:** `https://github.com/Swagata-Bhowmik/group4-mlflow-capstone`  
**Folder:** `/Users/krishsoni/Documents/swagata/ml-ops`  
**Current observed state:** Local repository initialized; all project files untracked; no commits exist. The assistant cannot write `.git` in its execution environment, so run these commands in the normal **Terminal app on this Mac**.

## Read this once before starting

This sequence groups the existing project into **six import commits**, alternating Swagata and Sumit. The existing implementation was prepared with AI assistance; the messages say so. These commits organize the import and do not prove that each member independently wrote the assigned files. Each member should review and authorize the material committed under their identity. Genuine individual contributions and the ability to explain/modify the project remain assignment requirements.

The wrappers select **commit author and committer**; they do not log in to two GitHub accounts. One authorized token can push the entire history, and GitHub records the push under that token's owner. Account attribution depends on each email being associated with the corresponding GitHub account. The wrappers do not add a verified cryptographic signature.

**Run the commands in order. Stop at any unexpected error. Do not use `git add .` midway: both wrappers share one staging area.** No push is needed between these six commits; push the completed import once at the end. Do not backdate commits or rewrite existing history to mimic past work.

## 1. Open the correct folder

Open **Terminal**, then enter:

```bash
cd "/Users/krishsoni/Documents/swagata/ml-ops"
```

Check the repository root:

```bash
git rev-parse --show-toplevel
```

Expected: the same project path shown above.

Check the branch and current state:

```bash
git branch --show-current
```

Expected: `main`. If a different branch is shown, do not rename or overwrite it blindly; check why before proceeding.

```bash
git status --short
```

The current files should appear as untracked (`??`). If you have already made commits since this guide was written, inspect `git log --oneline` and skip steps whose files are already committed rather than recreating the import.

Check for already staged changes:

```bash
git diff --cached --name-only
```

Expected: no output. If files appear, review what was previously staged. This guide assumes an empty staging area before each group.

## 2. Configure the two emails for this folder only

```bash
git config --local team.swagata.email "swagatabhowmik.28@gmail.com"
```

```bash
git config --local team.sumit.email "sumitkothari900@gmail.com"
```

Make sure the wrappers are executable:

```bash
chmod +x git-swagata git-sumit scripts/git-identity.sh
```

Confirm the identities without making a commit:

```bash
./git-swagata var GIT_AUTHOR_IDENT
```

Expected name/email: `Swagata Bhowmik <swagatabhowmik.28@gmail.com>` followed by a timestamp.

```bash
./git-sumit var GIT_AUTHOR_IDENT
```

Expected name/email: `Sumit Kothari <sumitkothari900@gmail.com>` followed by a timestamp.

These commands do not change global Git settings. No token is needed for any local commit below.

## 3. Connect the intended GitHub repository

Paste this block as one command block. It adds the remote if missing, or corrects it if already present:

```bash
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin https://github.com/Swagata-Bhowmik/group4-mlflow-capstone.git
else
  git remote add origin https://github.com/Swagata-Bhowmik/group4-mlflow-capstone.git
fi
```

The URL intentionally contains no token.

## 4. Commit 1 — Swagata: project foundations and supplied data

**Review before committing:** The assignment, unchanged CSVs, data fingerprints, dependency files, configuration and Git helpers. This commit imports the supplied material and prepared setup files; it does not claim the assignment/data were authored by the team.

Stage exactly this group:

```bash
./git-swagata add -- .gitignore .dockerignore git-swagata git-sumit scripts/git-identity.sh "Capstone End_to_End_Pipeline.docx" capstone_house_prices_train.csv capstone_incoming_batches.csv data_manifest.json requirements.txt requirements.lock config.yaml
```

Review the staged summary:

```bash
./git-swagata diff --cached --stat
```

Commit after review and authorization:

```bash
./git-swagata commit -m "Import supplied data and AI-assisted project foundations"
```

Verify the recorded author and committer:

```bash
git log -1 --format=fuller
```

Expected author/committer: Swagata.

## 5. Commit 2 — Sumit: initial model comparison

**Review before committing:** Four-model comparison, split membership, validation predictions and measured results. Sumit should be able to explain the split, MAE, and why Ridge was selected.

```bash
./git-sumit add -- experiments/baseline_config.yaml experiments/run_baselines.py experiments/baseline_results/results.json experiments/baseline_results/split_membership.csv experiments/baseline_results/validation_predictions.csv
```

```bash
./git-sumit diff --cached --stat
```

```bash
./git-sumit commit -m "Import AI-assisted baseline comparison and measured results"
```

```bash
git log -1 --format=fuller
```

Expected author/committer: Sumit.

## 6. Commit 3 — Swagata: pipeline, API and monitoring code

**Review before committing:** The eight stages, data/model gates, MLflow tracking, model switching, API, monitoring and demo code. No new cloud deployment is performed by this commit.

```bash
./git-swagata add -- capstone/
```

```bash
./git-swagata diff --cached --stat
```

```bash
./git-swagata commit -m "Import AI-assisted MLflow pipeline, serving API and monitoring"
```

```bash
git log -1 --format=fuller
```

Expected author/committer: Swagata.

## 7. Commit 4 — Sumit: tests and recorded local evidence

**Review before committing:** The 15 local tests, final-test result, batch reports, safe failures, rollback, lineage and reproduction evidence. These files describe actual local execution; they do not claim Docker/network/GitHub execution has occurred.

```bash
./git-sumit add -- tests/ reports/
```

The `.gitignore` excludes `*.log`; existing JSON/XML/HTML/TXT evidence is included. The complete transfer ZIP retains historical logs. Avoid force-adding all ignored logs or runtime state.

```bash
./git-sumit diff --cached --stat
```

```bash
./git-sumit commit -m "Import tests and measured local capstone evidence"
```

```bash
git log -1 --format=fuller
```

Expected author/committer: Sumit.

## 8. Commit 5 — Swagata: container and release configuration

**Review before committing:** Docker/Compose, Prometheus/Grafana, PR checks, Docker Hub publishing and deployment helpers. These are prepared infrastructure files; image publishing and host verification remain pending.

```bash
./git-swagata add -- Dockerfile compose.yaml .github/ monitoring/ scripts/deploy.sh scripts/generate_monitoring_config.py scripts/snapshot_registry.py scripts/check_reproduction.py
```

```bash
./git-swagata diff --cached --stat
```

```bash
./git-swagata commit -m "Import Docker, monitoring and Docker Hub release configuration"
```

```bash
git log -1 --format=fuller
```

Expected author/committer: Swagata.

## 9. Commit 6 — Sumit: documentation and handoff

**Review before committing:** The design note/reflection, operational instructions, presentation plan, current-status records and handoff. Earlier Windows instructions are retained as reference; this laptop is now the active Mac environment. Both students must review and understand the final reflection before submitting it.

```bash
./git-sumit add -- README.md PROJECT_CONTEXT.md START_HERE_PROJECT_HANDOFF.md WINDOWS_START_HERE.md COMMIT_COMMANDS_MAC.md docs/ output/pdf/ scripts/build_documents.py
```

```bash
./git-sumit diff --cached --stat
```

```bash
./git-sumit commit -m "Import AI-assisted design documents and project handoff guides"
```

```bash
git log -1 --format=fuller
```

Expected author/committer: Sumit.

## 10. Check the complete local history

```bash
git log --reverse --format='%h | %an <%ae> | %s'
```

Expected order: **Swagata → Sumit → Swagata → Sumit → Swagata → Sumit**, with the six import messages above. These are new current-time commits, not a reconstruction of past development history.

```bash
git status --short
```

Expected: no output for the files covered above. If new files appeared since this guide was generated, inspect them before staging. Ignored `.venv`, `.downloads`, runtime `state`, ZIPs and local setup scripts should not be committed.

The intermediate import commits are organizational groups; do not expect every partial group to run independently before all six groups are present. The final tree contains the complete project.

## 11. Push once using the existing authorized token

**Before pushing:** The repository should still be empty remotely. The initial push to `main` triggers the release workflow. That workflow requires `DOCKERHUB_USERNAME` and secret `DOCKERHUB_TOKEN`, as explained in `docs/DOCKER_HUB_DEPLOYMENT.md`. If those are not configured yet, the publishing workflow will fail its setup check even though the Git push succeeds. That is separate from Git authentication and does not require recreating commits.

Use this in the same interactive Mac Terminal:

```bash
git -c credential.helper= push -u origin main
```

If prompted:

- **Username:** GitHub username belonging to the token.
- **Password:** the token. Characters normally do not appear when entering it.

The empty credential-helper setting applies only to this command; the token is not stored by a helper through this invocation. Never put it directly in the command, remote URL, script, chat, or commit message. A local askpass dialog may be used depending on your Terminal setup.

The token owner must have write access. Because this push includes `.github/workflows/` files, the token needs the appropriate workflow-write permission as well as repository-content write permission. If GitHub rejects the push, read the error rather than granting unrelated privileges. A fine-grained token owned by an outside collaborator may also be limited by GitHub's token support/policies; use an appropriate authorized account/token configuration.

**One push uploads all six commits.** Using one token does not change their recorded authors, and it does not create two independently authenticated push events.

Do not use `--force` if the remote unexpectedly contains other work. Fetch and inspect the difference before deciding how to reconcile it.

## 12. Confirm on GitHub

1. Open `https://github.com/Swagata-Bhowmik/group4-mlflow-capstone`.
2. Confirm files and the six commits appear.
3. Confirm each email is linked to the intended account. If an author does not link, check that member's GitHub email settings before rewriting any history.
4. Open Actions. A successful Git push and a successful release workflow are different results.
5. Continue with Docker Hub setup and the actual PR/deployment evidence. These initial commits do **not** create a passing/failing PR demonstration, a published image, or a deployed server by themselves.
6. Revoke the temporary GitHub token when repository operations are finished. The Docker Hub publishing token is a separate credential; do not revoke it while the workflow still needs it.

## 13. What the assistant has and has not done

**Done:** Prepared the identity wrappers, local setup guide, this ordered file/commit plan, and the project files. Checked that the current file groups cover the intended untracked files.

**Not done:** No real project commits, remote setup or push were performed by the assistant. The execution environment still prevents writes to `.git`. This guide is for your own Mac Terminal, which already successfully initialized the repository.
