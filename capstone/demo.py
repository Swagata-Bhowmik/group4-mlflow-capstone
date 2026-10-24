"""Measured safe-failure, rollback, lineage, and API evidence with in-process HTTP."""
from pathlib import Path
from time import perf_counter
import json
import numpy as np
import pandas as pd
import yaml
from fastapi.testclient import TestClient
from .api import create_app
from .config import load, digest
from .core import GateError, pipeline, production, rollback, write_json, now


def demonstrate(config_path='config.yaml'):
    cfg=load(config_path); reports=Path(cfg.paths.reports); reports.mkdir(parents=True,exist_ok=True)
    fixture=Path(cfg.paths.state)/'demo_inputs'; fixture.mkdir(parents=True,exist_ok=True)
    sources={p:digest(p) for p in [cfg.paths.training,cfg.paths.incoming]}
    if production(cfg) is None: pipeline(config_path)
    client=TestClient(create_app(config_path))
    source=pd.read_csv(cfg.paths.training)
    records=json.loads(source[cfg.features.all].head(1).to_json(orient='records'))
    request={'records':records}
    initial=client.post('/predict',json=request); assert initial.status_code==200
    before=initial.json(); pointer=digest(Path(cfg.paths.state)/'production.json')
    bad=source.copy(); bad.loc[:int(len(bad)*.2),'Age_Years']=np.nan
    bad_path=fixture/'bad_missingness.csv'; bad.to_csv(bad_path,index=False)
    failures=[]
    for name in ['bad_data','bad_model']:
        config=config_path; input_path=None
        if name=='bad_data': input_path=bad_path
        else:
            badcfg=cfg.model_dump(); badcfg['model']['kind']='dummy'
            config=fixture/'bad_model.yaml'; config.write_text(yaml.safe_dump(badcfg,sort_keys=False), encoding='utf-8')
        try:
            pipeline(config,input_path)
        except GateError as exc:
            after=client.post('/predict',json=request)
            proof={'scenario':name,'gate_message':str(exc),'status':'PASSED','endpoint_status':after.status_code,
                   'before':before,'after':after.json(),'production_manifest_unchanged':digest(Path(cfg.paths.state)/'production.json')==pointer}
            assert after.status_code==200 and after.json()==before and proof['production_manifest_unchanged']
            failures.append(proof)
        else: raise AssertionError(f'{name} unexpectedly passed')
    write_json(reports/'safe_failures.json',{'at':now(),'transport':'FastAPI TestClient, in-process HTTP; not Docker/network uptime proof','scenarios':failures})
    # A second valid release makes rollback demonstrable without forcing a worse model.
    pipeline(config_path)
    second=client.get('/health').json()['model_version']
    assert second!=before['model_version']
    proof=rollback(cfg)
    restored=client.post('/predict',json=request)
    assert restored.json()==before
    proof.update({'endpoint_status':restored.status_code,'restored_prediction':restored.json(),'transport':'in-process HTTP'})
    write_json(reports/'rollback.json',proof)
    # Warm model already loaded. This measures TestClient round trips, not network capacity.
    timings=[]; failures_count=0
    for _ in range(cfg.monitoring.benchmark_requests):
        start=perf_counter(); response=client.post('/predict',json=request); timings.append(perf_counter()-start)
        failures_count+=response.status_code!=200
    invalid=client.post('/predict',json={'records':[{'Area_sqft':-1}]})
    assert invalid.status_code==422
    operational={'at':now(),'transport':'FastAPI TestClient in-process HTTP; warm, sequential single-row requests',
                 'requests':len(timings),'errors':failures_count,'error_rate':failures_count/len(timings),
                 'p50_seconds':float(np.quantile(timings,.5)),'p95_seconds':float(np.quantile(timings,.95)),
                 'observed_sequential_requests_per_second':len(timings)/sum(timings),
                 'invalid_request_status':invalid.status_code,'model_version':production(cfg)['version'],
                 'latency_target_passed':bool(np.quantile(timings,.95)<=cfg.monitoring.p95_latency_seconds),
                 'error_target_passed':failures_count/len(timings)<=cfg.monitoring.max_error_rate}
    write_json(reports/'operational.json',operational)
    (reports/'prometheus_metrics.txt').write_text(client.get('/metrics').text, encoding='utf-8')
    write_json(reports/'lineage.json',client.get('/lineage').json())
    assert sources=={p:digest(p) for p in sources}
    write_json(reports/'source_integrity.json',{'unchanged':True,'sha256':sources})
    # Report the restored serving version consistently after rollback.
    from .monitoring import monitor
    monitor(cfg)
    print(json.dumps({'failures':failures,'rollback':proof,'operational':operational},indent=2))
