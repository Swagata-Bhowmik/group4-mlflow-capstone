"""Fresh-clone reproduction: clone from GitHub, install the lockfile into a clean
virtual environment, run the tests and the pipeline to the model gate, and compare
the validation MAE with the recorded baseline within the configured tolerance.

Usage: python3.12 scripts/fresh_clone_reproduction.py [git-ref]
Writes reports/fresh_clone_reproduction.json in this checkout.
"""
import json
import platform
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = 'https://github.com/Swagata-Bhowmik/group4-mlflow-capstone.git'
root = Path(__file__).resolve().parents[1]
ref = sys.argv[1] if len(sys.argv) > 1 else 'main'
steps = []


def run(name, cmd, cwd, env=None):
    start = time.perf_counter()
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    steps.append({'step': name, 'command': ' '.join(map(str, cmd)), 'returncode': result.returncode,
                  'seconds': round(time.perf_counter() - start, 1), 'output_tail': (result.stdout + result.stderr)[-1500:]})
    print(f'[{name}] exit {result.returncode} in {steps[-1]["seconds"]} s', flush=True)
    if result.returncode:
        raise RuntimeError(f'{name} failed')
    return result.stdout


with tempfile.TemporaryDirectory(prefix='group4-fresh-clone-') as tmp:
    clone, venv = Path(tmp) / 'clone', Path(tmp) / 'venv'
    report = {'started': datetime.now(timezone.utc).isoformat(), 'repository': REPO, 'ref': ref,
              'host': f'{platform.system()} {platform.release()} {platform.machine()}',
              'bootstrap_python': sys.version.split()[0],
              'method': 'git clone from GitHub; new virtual environment WITHOUT system site packages; pip install -r requirements.lock'}
    try:
        run('clone', ['git', 'clone', '--quiet', REPO, str(clone)], tmp)
        run('checkout', ['git', 'checkout', '--quiet', ref], clone)
        report['commit'] = run('commit', ['git', 'rev-parse', 'HEAD'], clone).strip()
        run('create clean venv', [sys.executable, '-m', 'venv', str(venv)], tmp)
        python = str(venv / 'bin' / 'python')
        run('install locked dependencies', [python, '-m', 'pip', 'install', '--quiet', '--disable-pip-version-check', '-r', 'requirements.lock'], clone)
        report['installed_packages'] = len(run('pip freeze', [python, '-m', 'pip', 'freeze'], clone).splitlines())
        env = {'PATH': f'{venv}/bin:/usr/bin:/bin', 'HOME': tmp, 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'}
        tests = run('tests', [python, '-m', 'pytest', '-q', '-p', 'no:cacheprovider'], clone, env)
        report['tests'] = tests.strip().splitlines()[-1]
        run('pipeline to model gate', [python, '-m', 'capstone', 'run', '--stop-after', 'evaluate'], clone, env)
        evaluation = json.loads(next((clone / 'state' / 'runs').glob('*/evaluation.json')).read_text(encoding='utf-8'))
        expected = json.loads((clone / 'experiments/baseline_results/results.json').read_text(encoding='utf-8'))['results'][0]['validation_mae_lakhs']
        import yaml  # noqa: E402  (bootstrap interpreter only parses the cloned config)
        tolerance = yaml.safe_load((clone / 'config.yaml').read_text(encoding='utf-8'))['quality']['reproducibility_tolerance']
        delta = abs(expected - evaluation['metrics']['mae'])
        report.update({'expected_validation_mae': expected, 'reproduced_validation_mae': evaluation['metrics']['mae'],
                       'reproduced_validation_rmse': evaluation['metrics']['rmse'], 'absolute_difference': delta,
                       'tolerance': tolerance, 'passed': delta <= tolerance})
    except Exception as exc:
        report.update({'passed': False, 'error': str(exc)})
    report['finished'] = datetime.now(timezone.utc).isoformat()
    report['steps'] = steps
    (root / 'reports' / 'fresh_clone_reproduction.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report.get(k) for k in ['commit', 'tests', 'reproduced_validation_mae', 'absolute_difference', 'passed', 'error']}, indent=2))
    sys.exit(0 if report['passed'] else 1)
