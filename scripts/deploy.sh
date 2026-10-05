#!/usr/bin/env bash
# Run from repository root on a Docker host. CAPSTONE_IMAGE must identify a release image, preferably by digest.
set -euo pipefail
: "${CAPSTONE_IMAGE:?Set CAPSTONE_IMAGE to the Docker Hub image digest or commit tag}"
previous_image="$(docker inspect --format '{{.Config.Image}}' "$(docker compose ps -q api)" 2>/dev/null || true)"
docker compose pull api pipeline mlflow
# A rejected candidate stops here. Existing API container continues serving.
docker compose --profile jobs run --rm -e GITHUB_SHA="${GITHUB_SHA:-uncommitted-local-source}" pipeline
if docker compose up -d --wait api mlflow prometheus grafana; then
  printf 'Deployment healthy: %s\n' "$CAPSTONE_IMAGE"
else
  docker compose --profile jobs run --rm pipeline python -m capstone rollback
  if [ -n "$previous_image" ]; then
    export CAPSTONE_IMAGE="$previous_image"
    docker compose up -d --wait api mlflow prometheus grafana
  fi
  exit 1
fi
