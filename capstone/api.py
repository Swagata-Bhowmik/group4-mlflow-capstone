import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from .config import digest, load
from .core import STAGES, GateError, production, read_json, validate_frame


def create_app(config_path=None):
    cfg=load(config_path or os.environ.get('CAPSTONE_CONFIG','config.yaml'))
    app=FastAPI(title='Group 4 · House Price API',version='1.0.0')
    registry=CollectorRegistry()
    requests=Counter('prediction_requests_total','Prediction HTTP requests',['status'],registry=registry)
    latency=Histogram('prediction_latency_seconds','Prediction request latency',buckets=cfg.monitoring.latency_buckets,registry=registry)
    prices=Histogram('predicted_price_lakhs','Distribution of predicted asking prices',buckets=cfg.monitoring.prediction_buckets,registry=registry)
    reload_failures=Counter('model_reload_failures_total','Failed candidate loads; last healthy model retained',registry=registry)
    age=Gauge('model_age_days','Age of serving model',registry=registry)
    model_info=Gauge('serving_model_info','Currently loaded version',['version'],registry=registry)
    lock=threading.Lock(); cache={'model':None,'manifest':None}

    def current():
        with lock:
            candidate=production(cfg)
            if candidate is None and cache['model'] is None: raise HTTPException(503,'No production model')
            if candidate and (cache['manifest'] is None or candidate['model_sha256']!=cache['manifest']['model_sha256'] or candidate['version']!=cache['manifest']['version']):
                try:
                    if digest(candidate['model_path'])!=candidate['model_sha256']: raise ValueError('Artifact integrity mismatch')
                    model=joblib.load(candidate['model_path'])
                    cache.update(model=model,manifest=candidate)
                    model_info.clear(); model_info.labels(candidate['version']).set(1)
                except Exception:
                    reload_failures.inc()
                    if cache['model'] is None: raise HTTPException(503,'Production artifact unavailable')
            manifest=cache['manifest']
            age.set((datetime.now(timezone.utc)-datetime.fromisoformat(manifest['deployed_at'])).total_seconds()/86400)
            return cache['model'],manifest

    @app.middleware('http')
    async def observe(request:Request, call_next):
        if request.url.path!='/predict': return await call_next(request)
        start=time.perf_counter(); status='500'
        try:
            response=await call_next(request); status=str(response.status_code); return response
        finally:
            latency.observe(time.perf_counter()-start); requests.labels(status).inc()

    @app.get('/health')
    def health():
        _,manifest=current()
        return {'status':'ok','model_version':manifest['version'],'mlflow_run_id':manifest['mlflow_run_id']}

    @app.get('/lineage')
    def lineage():
        _,manifest=current()
        return {k:manifest[k] for k in ['version','mlflow_run_id','source','data','configuration','validation','deployed_at','model_sha256']}

    @app.post('/predict')
    def predict(payload:dict):
        if set(payload)!={'records'} or not isinstance(payload['records'],list): raise HTTPException(422,'Supply only a records array')
        records=payload['records']
        if not 1<=len(records)<=cfg.serving.max_batch_size or any(not isinstance(r,dict) or set(r)!=set(cfg.features.all) for r in records):
            raise HTTPException(422,'Invalid batch size or feature schema')
        df=pd.DataFrame(records)
        try: validate_frame(df,cfg,prediction=True)
        except (GateError,TypeError,ValueError) as exc: raise HTTPException(422,str(exc)) from exc
        model,manifest=current()
        predictions=model.predict(df[cfg.features.all])
        if not np.isfinite(predictions).all(): raise HTTPException(503,'Invalid model output')
        for value in predictions: prices.observe(float(value))
        return {'model_version':manifest['version'],'price_lakhs':predictions.tolist()}

    @app.get('/metrics')
    def prometheus():
        try: current()
        except HTTPException: pass
        return Response(generate_latest(registry),media_type=CONTENT_TYPE_LATEST)

    # Read-only views for the dashboard. They report recorded evidence; none of them change the model.
    started=time.time()

    @app.get('/',include_in_schema=False)
    def dashboard(): return FileResponse(Path(__file__).with_name('static')/'dashboard.html')

    @app.get('/schema')
    def schema():
        s=cfg.data_schema
        return {'numeric':[{'name':c,'range':s.ranges[c],'integer':c in s.integers,'optional':c in s.missing_allowed} for c in cfg.features.numeric],
                'categorical':[{'name':c,'categories':s.categories[c],'optional':c in s.missing_allowed} for c in cfg.features.categorical],
                'max_batch_size':cfg.serving.max_batch_size,'quality':cfg.quality.model_dump(),'monitoring':cfg.monitoring.model_dump()}

    def run_file(name):
        _,manifest=current(); path=Path(manifest['run_directory'])/name
        if not path.exists(): raise HTTPException(404,f'{name} was not recorded for the serving model')
        return read_json(path)

    @app.get('/pipeline')
    def pipeline_run():
        meta=run_file('run.json')
        return {'run_id':meta['id'],'mlflow_run_id':meta['mlflow_run_id'],'created':meta['created'],'status':meta['status'],'stages':STAGES,
                'results':{k:{'status':v['status'],'seconds':v['seconds'],'at':v['at'],'error':v.get('error')} for k,v in meta['stages'].items()},
                'evaluation':run_file('evaluation.json')}

    @app.get('/monitoring')
    def monitoring(): return run_file('monitoring.json')

    @app.get('/samples')
    def samples(batch:int, n:int=5):
        if batch not in (1,2,3) or not 1<=n<=20: raise HTTPException(422,'Choose batch 1-3 and 1-20 rows')
        df=pd.read_csv(cfg.paths.incoming); df=df[df.Batch==batch].sample(n)
        # to_json turns NaN into null, which /predict accepts for nullable columns.
        records=json.loads(df[cfg.features.all].to_json(orient='records'))
        return {'batch':batch,'house_ids':df[cfg.features.identifier].tolist(),'records':records,'actual_price_lakhs':df[cfg.features.target].tolist()}

    @app.get('/stats')
    def stats():
        def buckets(name):
            rows=[(float(s.labels['le']) if s.labels['le']!='+Inf' else None,s.value) for m in registry.collect() if m.name==name for s in m.samples if s.name==name+'_bucket']
            return [{'le':le,'count':c-prev} for (le,c),prev in zip(rows,[0]+[c for _,c in rows[:-1]])]
        by_status={s.labels['status']:s.value for m in registry.collect() if m.name=='prediction_requests' for s in m.samples if s.name=='prediction_requests_total'}
        total=sum(by_status.values()); seconds=registry.get_sample_value('prediction_latency_seconds_sum') or 0
        lat=buckets('prediction_latency_seconds'); p95=None; seen=0
        for b in lat:
            seen+=b['count']
            if total and seen>=0.95*total: p95=b['le']; break
        uptime=time.time()-started
        return {'uptime_seconds':uptime,'requests':total,'by_status':by_status,'errors':sum(v for k,v in by_status.items() if not k.startswith('2')),
                'requests_per_minute':total/uptime*60,'mean_latency_seconds':seconds/total if total else None,'p95_latency_bucket_seconds':p95,
                'latency_buckets':lat,'predicted_price_buckets':buckets('predicted_price_lakhs'),'reload_failures':registry.get_sample_value('model_reload_failures_total')}
    return app
