#!/usr/bin/env bash
# Build the submission package: repository link + the deliverables from the brief (no source code).
# Usage: bash scripts/build_submission.sh   ->  group4_capstone_submission.zip
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || { echo "Commit your changes first."; exit 1; }

REPO=https://github.com/Swagata-Bhowmik/group4-mlflow-capstone
LIVE=https://group4-mlflow-capstone.onrender.com
OUT=group4_capstone_submission
tmp=$(mktemp -d); pkg="$tmp/$OUT"
mkdir -p "$pkg"/{1_design_note,2_screenshots,3_failing_gate_evidence,4_lineage,5_ci_history,6_monitoring,7_reflection,8_demonstration}

cp output/pdf/design_note.pdf "$pkg/1_design_note/"
cp output/screenshots/0[1-4]_*.png "$pkg/2_screenshots/"
cp reports/live_safe_failures.json reports/safe_failures.json output/screenshots/12_dashboard_rejected_input.png "$pkg/3_failing_gate_evidence/"
cp output/screenshots/05_live_lineage.png output/screenshots/04_mlflow_run_detail.png "$pkg/4_lineage/"
# Snapshot of the live model's lineage at build time (code commit, MLflow run, data hash, config).
curl -fsS -m 120 "$LIVE/lineage" | python3 -m json.tool > "$pkg/4_lineage/live_lineage.json" || echo "Live lineage unavailable; skipped."
cp output/screenshots/2[0-4]_*.png reports/render_rollback.json "$pkg/5_ci_history/"
cp reports/monitoring.html reports/monitoring.json reports/load_test.json output/screenshots/1[0134]_*.png output/screenshots/15_*.png "$pkg/6_monitoring/"
cp output/pdf/reflection.pdf "$pkg/7_reflection/"

cat > "$pkg/README.md" <<EOF
# Group 4 · Project 4 Capstone: End-to-End MLflow Pipeline

Swagata Bhowmik (B053) · Sumit Kothari (B062) · Dr. Santosh Kumar

- **Repository:** $REPO (pipeline, configuration, tests, workflows, Dockerfile, README)
- **Live dashboard:** $LIVE/ (free host; first load can take about a minute)
- **Live lineage:** $LIVE/lineage · **API docs:** $LIVE/docs
- **Demonstration video:** see 8_demonstration/

| Deliverable | In this package |
|---|---|
| Repository | Link above |
| Design note (2 pages) with architecture diagram | 1_design_note/design_note.pdf |
| Workflow graph, run history, registry screenshots | 2_screenshots/ (01 workflow graph, 02 MLflow run history, 03 registry, 04 run detail) |
| Two failing-gate scenarios | 3_failing_gate_evidence/: bad data stopped at validate and bad model at evaluate while the live server kept serving (live_safe_failures.json); in-process run (safe_failures.json); invalid input rejected |
| Lineage demonstration | Live at $LIVE/ (Lineage tab) and in the video; screenshots and deployment record in 4_lineage/ |
| CI history with releases | $REPO/actions and $REPO/releases; screenshots in 5_ci_history/ (PR #2 failed at the model gate, then fixed); live rollback test (render_rollback.json) |
| Monitoring covering the three batches | 6_monitoring/monitoring.html (open in a browser), monitoring.json, dashboard screenshots, load test |
| 5–10 minute demonstration | 8_demonstration/ |
| Reflection (1 page) | 7_reflection/reflection.pdf |

Built from commit $(git rev-parse --short HEAD).
EOF
echo "Place the demonstration video (or a text file with its link) in this folder." > "$pkg/8_demonstration/README.txt"

rm -f "$OUT.zip"
(cd "$tmp" && zip -qr - "$OUT") > "$OUT.zip"
rm -rf "$tmp"
echo "Built $OUT.zip ($(du -h "$OUT.zip" | cut -f1)) from $(git rev-parse --short HEAD)"
