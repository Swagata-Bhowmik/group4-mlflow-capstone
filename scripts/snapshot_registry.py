"""Export actual MLflow records for portable evidence, not fabricated UI screenshots."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run from any folder, no PYTHONPATH needed
from capstone.config import load
from capstone.core import setup_tracking, write_json
cfg=load();client,eid=setup_tracking(cfg)
runs=[{'id':r.info.run_id,'status':r.info.status,'metrics':r.data.metrics,'tags':r.data.tags} for r in client.search_runs([eid])]
versions=[{'version':v.version,'run_id':v.run_id,'status':v.status,'tags':v.tags,'source':v.source} for v in client.search_model_versions(f"name='{cfg.tracking.registered_model}'")]
write_json(Path(cfg.paths.reports)/'registry.json',{'experiment_id':eid,'runs':runs,'versions':versions,'champion':client.get_model_version_by_alias(cfg.tracking.registered_model,'champion').version})
