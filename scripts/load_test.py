"""Network workload against a deployed API: latency, throughput and errors over real HTTP.

Workload (documented so it can be repeated):
  1. one warm-up /health call (records the free-host cold-start time),
  2. a sequential phase of N single-listing predictions,
  3. a concurrent phase of W workers each sending M single-listing predictions,
  4. a small invalid-request phase that must be rejected with 422.
Listings are drawn from the supplied training file (seed 42), rotated per request.

Usage: python scripts/load_test.py [--url URL] [--sequential 100] [--workers 5] [--per-worker 40]
Writes reports/load_test.json.
"""
import argparse
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from capstone.config import load  # noqa: E402
from capstone.core import now, write_json  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument('--url', default='https://group4-mlflow-capstone.onrender.com')
p.add_argument('--sequential', type=int, default=100); p.add_argument('--workers', type=int, default=5); p.add_argument('--per-worker', type=int, default=40)
args = p.parse_args(); cfg = load()
records = json.loads(pd.read_csv(cfg.paths.training).sample(200, random_state=cfg.seed)[cfg.features.all].to_json(orient='records'))


def call(path, body=None):
    req = urllib.request.Request(args.url + path, data=json.dumps(body).encode() if body else None,
                                 headers={'Content-Type': 'application/json'}, method='POST' if body else 'GET')
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=60) as r: r.read(); return r.status, time.perf_counter() - start
    except urllib.error.HTTPError as e: return e.code, time.perf_counter() - start
    except OSError: return None, time.perf_counter() - start


def summary(results, wall):
    lat = np.array([s for _, s in results]); ok = [c for c, _ in results if c == 200]
    return {'requests': len(results), 'succeeded': len(ok), 'errors': len(results) - len(ok), 'error_rate': (len(results) - len(ok)) / len(results),
            'wall_seconds': round(wall, 2), 'throughput_rps': round(len(results) / wall, 2),
            **{f'p{q}_ms': round(float(np.quantile(lat, q / 100)) * 1000, 1) for q in (50, 95, 99)}, 'max_ms': round(float(lat.max()) * 1000, 1)}


report = {'at': now(), 'target': args.url, 'client': 'Python urllib from the team laptop over the public internet',
          'workload': {'sequential_requests': args.sequential, 'concurrent_workers': args.workers, 'requests_per_worker': args.per_worker,
                       'payload': 'one listing per request, rotated over 200 training listings (seed 42)'}}
def server_stats():
    with urllib.request.urlopen(args.url + '/stats', timeout=60) as r: return json.loads(r.read())


code, seconds = call('/health'); stats_before = server_stats(); report['warmup'] = {'status': code, 'seconds': round(seconds, 2), 'note': 'includes free-host wake-up if the service was idle'}
print('warm-up', report['warmup'], flush=True)

start = time.perf_counter(); seq = [call('/predict', {'records': [records[i % len(records)]]}) for i in range(args.sequential)]
report['sequential'] = summary(seq, time.perf_counter() - start); print('sequential', report['sequential'], flush=True)

def worker(w): return [call('/predict', {'records': [records[(w * args.per_worker + i) % len(records)]]}) for i in range(args.per_worker)]
start = time.perf_counter()
with ThreadPoolExecutor(args.workers) as pool: conc = [r for batch in pool.map(worker, range(args.workers)) for r in batch]
report['concurrent'] = summary(conc, time.perf_counter() - start); print('concurrent', report['concurrent'], flush=True)

# Server-side view of exactly this test: difference of the API's own latency histogram.
stats_after = server_stats()
buckets = [(a['le'], a['count'] - b['count']) for a, b in zip(stats_after['latency_buckets'], stats_before['latency_buckets'])]
counted, seen, p95_bucket = sum(c for _, c in buckets), 0, None
for le, c in buckets:
    seen += c
    if counted and seen >= 0.95 * counted: p95_bucket = le; break
report['server_side'] = {'requests_counted': counted, 'mean_ms': round((stats_after['mean_latency_seconds'] * stats_after['requests'] - (stats_before['mean_latency_seconds'] or 0) * stats_before['requests']) / counted * 1000, 1) if counted else None,
                         'p95_bucket_upper_ms': p95_bucket * 1000 if p95_bucket else None, 'buckets_ms': [{'le_ms': le * 1000 if le else None, 'count': c} for le, c in buckets],
                         'note': 'Measured inside the API (includes queueing in the single Uvicorn worker), from /stats before and after the valid-request phases.'}
print('server-side', {k: v for k, v in report['server_side'].items() if k != 'buckets_ms'}, flush=True)

invalid = [call('/predict', {'records': [{**records[0], 'Bedrooms': 0}]})[0] for _ in range(5)]
report['invalid_requests'] = {'sent': len(invalid), 'rejected_with_422': invalid.count(422)}
mon = cfg.monitoring; allp = seq + conc; lat95 = float(np.quantile([s for _, s in allp], .95))
err = sum(c != 200 for c, _ in allp) / len(allp)
report['targets'] = {'p95_latency_target_ms': mon.p95_latency_seconds * 1000, 'observed_p95_ms_all_valid_requests': round(lat95 * 1000, 1),
                     'server_side_p95_bucket_ms': report['server_side']['p95_bucket_upper_ms'],
                     'server_side_p95_target_met': bool(report['server_side']['p95_bucket_upper_ms'] and report['server_side']['p95_bucket_upper_ms'] <= mon.p95_latency_seconds * 1000),
                     'p95_target_met_end_to_end': lat95 <= mon.p95_latency_seconds, 'error_rate_target': mon.max_error_rate,
                     'observed_error_rate': err, 'error_target_met': err <= mon.max_error_rate,
                     'note': 'End-to-end times include internet round trip and TLS from the client; the configured target was set for server-side latency.'}
write_json(Path(cfg.paths.reports) / 'load_test.json', report)
print(json.dumps(report['targets'], indent=2))
