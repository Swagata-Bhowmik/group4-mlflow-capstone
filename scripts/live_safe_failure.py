"""Safe-failure proof against a real HTTP server process (not the in-process TestClient).

Starts the API with Uvicorn as a separate process, keeps sending prediction requests
over TCP while two bad pipeline runs execute (bad data, then a bad model), and records
that both gates stop the run while the endpoint keeps serving the same model.

Usage: python scripts/live_safe_failure.py [--port 8765]
Writes reports/live_safe_failures.json.
"""
import argparse
import json
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from capstone.config import digest, load  # noqa: E402
from capstone.core import now, write_json  # noqa: E402

p = argparse.ArgumentParser(); p.add_argument('--port', type=int, default=8765); p.add_argument('--config', default='config.yaml')
args = p.parse_args()
cfg = load(args.config); base = f'http://127.0.0.1:{args.port}'
state = Path(cfg.paths.state); fixture = state / 'demo_inputs'; fixture.mkdir(parents=True, exist_ok=True)


def call(path, body=None):
    req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body else None,
                                 headers={'Content-Type': 'application/json'}, method='POST' if body else 'GET')
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=10) as r: return r.status, json.loads(r.read()), time.perf_counter() - start
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read() or b'null'), time.perf_counter() - start


server = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'capstone.api:create_app', '--factory', '--host', '127.0.0.1', '--port', str(args.port)],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env={**__import__('os').environ, 'CAPSTONE_CONFIG': args.config})
try:
    for _ in range(100):
        try:
            if call('/health')[0] == 200: break
        except OSError: time.sleep(0.2)
    else: raise RuntimeError('Server did not start')

    record = json.loads(pd.read_csv(cfg.paths.training)[cfg.features.all].head(1).to_json(orient='records'))
    request = {'records': record}

    def snapshot():
        health = call('/health')[1]; lineage = call('/lineage')[1]; status, pred, _ = call('/predict', request)
        return {'model_version': health['model_version'], 'mlflow_run_id': health['mlflow_run_id'], 'model_sha256': lineage['model_sha256'],
                'prediction_status': status, 'price_lakhs': pred['price_lakhs'][0], 'production_pointer_sha256': digest(state / 'production.json')}

    # Background traffic: proves the endpoint answered continuously during each failing run.
    traffic = {'requests': 0, 'errors': 0, 'versions': set(), 'latencies': []}; stop = threading.Event()

    def load_loop():
        while not stop.is_set():
            try:
                status, body, seconds = call('/predict', request)
                traffic['requests'] += 1; traffic['latencies'].append(seconds)
                if status != 200: traffic['errors'] += 1
                else: traffic['versions'].add(body['model_version'])
            except OSError: traffic['requests'] += 1; traffic['errors'] += 1
            time.sleep(0.05)

    bad = pd.read_csv(cfg.paths.training); bad.loc[:int(len(bad) * .2), 'Age_Years'] = np.nan
    bad_data = fixture / 'bad_missingness.csv'; bad.to_csv(bad_data, index=False)
    badcfg = cfg.model_dump(by_alias=True); badcfg['model']['kind'] = 'dummy'
    bad_model = fixture / 'bad_model.yaml'; bad_model.write_text(yaml.safe_dump(badcfg, sort_keys=False), encoding='utf-8')
    scenarios = [('bad_data', 'Training file with 20% of Age_Years blanked (limit 8%)', ['--config', args.config, 'run', '--input', str(bad_data)]),
                 ('bad_model', 'Configuration switched to a median-only dummy model', ['--config', str(bad_model), 'run'])]
    results = []
    for name, change, cli in scenarios:
        before = snapshot(); traffic.update(requests=0, errors=0, versions=set(), latencies=[]); stop.clear()
        worker = threading.Thread(target=load_loop); worker.start()
        run = subprocess.run([sys.executable, '-m', 'capstone', *cli], capture_output=True, text=True)
        time.sleep(1); stop.set(); worker.join()
        after = snapshot()
        failed_stage = ([json.loads(l)['stage'] for l in run.stdout.splitlines() if l.startswith('{')] or [None])[-1]
        message = (run.stderr.strip().splitlines() or [''])[-1]
        results.append({'scenario': name, 'change': change, 'command': 'python -m capstone ' + ' '.join(cli),
                        'pipeline_exit_code': run.returncode, 'last_passed_stage': failed_stage, 'gate_message': message,
                        'before': before, 'after': after,
                        'traffic_during_run': {'requests': traffic['requests'], 'errors': traffic['errors'],
                                               'model_versions_served': sorted(traffic['versions']),
                                               'p95_ms': round(float(np.quantile(traffic['latencies'], .95)) * 1000, 2) if traffic['latencies'] else None},
                        'production_unchanged': before == after,
                        'passed': run.returncode != 0 and before == after and traffic['errors'] == 0})
        print(f"{name}: exit {run.returncode}, gate: {message[-120:]}, served {traffic['requests']} requests, errors {traffic['errors']}, unchanged {before == after}", flush=True)
    write_json(Path(cfg.paths.reports) / 'live_safe_failures.json', {
        'at': now(), 'transport': f'Real HTTP over TCP to a separate Uvicorn process at {base}', 'all_passed': all(r['passed'] for r in results), 'scenarios': results})
finally:
    server.terminate(); server.wait(10)
