"""Test the live rollback path end to end and record the evidence.

1. Record the live commit (from /lineage) and a reference prediction.
2. Dispatch the "Roll back Render deployment" workflow to an earlier released commit; wait.
3. Verify the live service now reports that commit.
4. Dispatch the same workflow back to the original commit (roll forward); wait and verify.

Needs a GitHub token with Actions write access in the GH_TOKEN environment variable.
Usage: GH_TOKEN=... python scripts/render_rollback_test.py <earlier-released-full-sha>
Writes reports/render_rollback.json.
"""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = 'Swagata-Bhowmik/group4-mlflow-capstone'
LIVE = 'https://group4-mlflow-capstone.onrender.com'
token = os.environ['GH_TOKEN']; target = sys.argv[1]
assert len(target) == 40, 'Give the full 40-character SHA'
record = {'started': datetime.now(timezone.utc).isoformat(), 'workflow': '.github/workflows/rollback.yml', 'service': LIVE, 'steps': []}
sample = {'records': [{'Area_sqft': 1200, 'Bedrooms': 2, 'Bathrooms': 2, 'Age_Years': 5, 'Distance_to_Center_km': 8,
                       'Neighborhood_Score': 7, 'Has_Parking': 1, 'Property_Condition': 'Good', 'City_Zone': 'Central'}]}


def gh(method, path, body=None):
    req = urllib.request.Request('https://api.github.com' + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read(); return json.loads(raw) if raw else None


def live(path, body=None):
    req = urllib.request.Request(LIVE + path, data=json.dumps(body).encode() if body else None, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=90) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, None


def snapshot():
    _, lineage = live('/lineage'); status, pred = live('/predict', sample)
    return {'commit': lineage['source']['commit'], 'model_version': lineage['version'], 'mlflow_run_id': lineage['mlflow_run_id'],
            'deployed_at': lineage['deployed_at'], 'predict_status': status, 'price_lakhs': pred['price_lakhs'][0] if pred else None,
            'dashboard_status': dashboard_status()}


def dashboard_status():
    try:
        with urllib.request.urlopen(LIVE + '/', timeout=90) as r: return r.status
    except urllib.error.HTTPError as e: return e.code


def deploy(commit, label):
    since = datetime.now(timezone.utc).isoformat(timespec='seconds')
    gh('POST', f'/repos/{REPO}/actions/workflows/rollback.yml/dispatches', {'ref': 'main', 'inputs': {'commit': commit}})
    start = time.monotonic(); run = None
    while time.monotonic() - start < 35 * 60:
        time.sleep(20)
        if run is None:
            runs = gh('GET', f'/repos/{REPO}/actions/workflows/rollback.yml/runs?event=workflow_dispatch&per_page=5')['workflow_runs']
            run = next((r for r in runs if r['created_at'] >= since), None)
            continue
        run = gh('GET', f'/repos/{REPO}/actions/runs/{run["id"]}')
        if run['status'] == 'completed': break
    minutes = (time.monotonic() - start) / 60
    after = snapshot()
    step = {'step': label, 'requested_commit': commit, 'workflow_run': run and run['html_url'], 'conclusion': run and run['conclusion'],
            'minutes': round(minutes, 1), 'live_after': after, 'verified': bool(run and run['conclusion'] == 'success' and after['commit'] == commit)}
    record['steps'].append(step); print(json.dumps(step, indent=2), flush=True)
    if not step['verified']: raise SystemExit(f'{label} did not verify')
    return step


before = snapshot(); record['live_before'] = before; print('live before', before, flush=True)
assert before['commit'] != target, 'Target is already live'
try:
    back = deploy(target, 'rollback'); fwd = deploy(before['commit'], 'roll forward')
    record.update({'from_commit': before['commit'], 'to_commit': target, 'rollback_minutes': back['minutes'],
                   'rollforward_minutes': fwd['minutes'], 'passed': True})
finally:
    record['finished'] = datetime.now(timezone.utc).isoformat()
    record.setdefault('passed', False)
    Path('reports/render_rollback.json').write_text(json.dumps(record, indent=2) + '\n')
