#!/usr/bin/env bash
# Build the submission ZIP from the committed state of the current branch (no local state, secrets or venv).
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || { echo "Commit your changes first."; exit 1; }
git archive --format=zip --prefix=group4-mlflow-capstone/ -o group4_capstone_submission.zip HEAD
echo "Built group4_capstone_submission.zip from $(git rev-parse --short HEAD)"
