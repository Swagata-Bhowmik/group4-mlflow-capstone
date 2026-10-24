"""Check a fresh directory copy with the SAME interpreter, not a clean-install claim."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import yaml
from capstone.core import write_json

root=Path.cwd()
with tempfile.TemporaryDirectory(prefix='group4-reproduction-') as tmp:
 dest=Path(tmp)
 shutil.copytree(root/'capstone',dest/'capstone',ignore=shutil.ignore_patterns('__pycache__'))
 for name in ['config.yaml','requirements.txt','capstone_house_prices_train.csv','capstone_incoming_batches.csv']:
  shutil.copyfile(root/name,dest/name)
 result=subprocess.run([sys.executable,'-m','capstone','run','--stop-after','evaluate'],cwd=dest,capture_output=True,text=True)
 (root/'reports/reproduction.log').write_text(result.stdout+'\n'+result.stderr, encoding='utf-8')
 if result.returncode:raise RuntimeError('Reproduction failed; inspect reports/reproduction.log')
 runs=list((dest/'state/runs').iterdir());evaluation=json.loads((runs[0]/'evaluation.json').read_text(encoding='utf-8'))
 expected=json.loads((root/'experiments/baseline_results/results.json').read_text(encoding='utf-8'))['results'][0]['validation_mae_lakhs']
 tolerance=yaml.safe_load((root/'config.yaml').read_text(encoding='utf-8'))['quality']['reproducibility_tolerance']
 delta=abs(expected-evaluation['metrics']['mae'])
 write_json(root/'reports/reproduction.json',{'method':'Fresh directory copy; same existing interpreter/dependencies. Not a fresh clone or clean dependency installation.','passed':delta<=tolerance,'expected_mae':expected,'actual_mae':evaluation['metrics']['mae'],'absolute_difference':delta,'tolerance':tolerance})
 assert delta<=tolerance
 print('Fresh-directory reproduction passed; MAE difference',delta)
