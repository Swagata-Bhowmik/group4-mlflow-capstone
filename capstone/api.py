import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from .config import digest, load
from .core import GateError, production, validate_frame


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
    return app
