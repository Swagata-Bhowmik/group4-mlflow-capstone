"""Persisted DAG stages. Only this module's deployment operations change production."""
import contextlib
import hashlib
import json
import os
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:  # POSIX file locks; Windows uses msvcrt below.
    import fcntl
except ImportError:
    fcntl = None
    import msvcrt

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow import MlflowClient
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import Config, digest, load

STAGES = ['ingest', 'validate', 'features', 'train', 'evaluate', 'register', 'deploy', 'monitor']
DEPENDENCIES = {s: STAGES[i-1:i] for i, s in enumerate(STAGES)}
ARTIFACTS = {'ingest':['raw.csv','data.json'], 'validate':[], 'features':['train.csv','validation.csv','test.csv'], 'train':['model.joblib'], 'evaluate':['evaluation.json'], 'register':['registration.json'], 'deploy':[], 'monitor':['monitoring.json']}
class GateError(ValueError): pass

def now(): return datetime.now(timezone.utc).isoformat()

def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    os.replace(temp, path)

def read_json(path): return json.loads(Path(path).read_text(encoding='utf-8'))

def setup_tracking(cfg):
    state = Path(cfg.paths.state).resolve(); state.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri('sqlite:///' + (state / 'mlflow.db').as_posix())
    client = MlflowClient()
    exp = client.get_experiment_by_name(cfg.tracking.experiment)
    eid = exp.experiment_id if exp else client.create_experiment(cfg.tracking.experiment, artifact_location=(state/'mlartifacts').as_uri())
    return client, eid

@contextlib.contextmanager
def deployment_lock(cfg):
    path = Path(cfg.paths.state); path.mkdir(parents=True, exist_ok=True)
    with (path/'deployment.lock').open('a+') as f:
        if fcntl: fcntl.flock(f, fcntl.LOCK_EX)
        else: f.seek(0); msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
        try: yield
        finally:
            if fcntl: fcntl.flock(f, fcntl.LOCK_UN)
            else: f.seek(0); msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)

def production(cfg):
    path = Path(cfg.paths.state)/'production.json'
    return read_json(path) if path.exists() else None

def code_snapshot():
    paths = sorted([*Path('capstone').glob('*.py'), Path('requirements.txt')])
    hashes = {p.as_posix(): digest(p) for p in paths if p.exists()}
    return {'sha256': hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest(),
            'files': hashes, 'commit': os.environ.get('GITHUB_SHA', 'uncommitted-local-source')}

def validate_frame(df, cfg, prediction=False):
    expected = cfg.features.all if prediction else cfg.features.all + [cfg.features.identifier, cfg.features.target]
    errors = []
    if set(df.columns) != set(expected): raise GateError('Schema columns do not match: ' + str(sorted(set(df.columns)^set(expected))))
    if len(df) == 0 or (not prediction and len(df) < cfg.data_schema.min_rows): errors.append('Insufficient rows')
    if not prediction:
        ids = df[cfg.features.identifier]
        if ids.isna().any() or ids.astype(str).str.strip().eq('').any() or ids.duplicated().any(): errors.append('IDs missing or duplicated')
    for col in expected:
        missing = df[col].isna()
        if col not in cfg.data_schema.missing_allowed and missing.any(): errors.append(f'{col}: required value missing')
        if not prediction and missing.mean() > cfg.data_schema.max_missing_fraction: errors.append(f'{col}: missing fraction exceeds limit')
    for col, (low, high) in cfg.data_schema.ranges.items():
        if col not in df: continue
        x = pd.to_numeric(df[col], errors='coerce')
        # Reject text/bool inputs even if they can be silently coerced into numbers.
        invalid_type = df[col].dropna().map(lambda v: isinstance(v, (str, bool))).any()
        if invalid_type or (x.isna() & df[col].notna()).any(): errors.append(f'{col}: nonnumeric value')
        observed = x.dropna()
        if not np.isfinite(observed).all() or not observed.between(low, high).all(): errors.append(f'{col}: outside allowed range')
        if col in cfg.data_schema.integers and (observed % 1 != 0).any(): errors.append(f'{col}: fractional integer')
    for col, categories in cfg.data_schema.categories.items():
        if (~df[col].dropna().isin(categories)).any(): errors.append(f'{col}: unknown category')
    if errors: raise GateError('; '.join(errors))
    return {'rows':len(df), 'missing_fraction':df.isna().mean().to_dict(), 'passed':True}

def estimator(cfg):
    numeric = Pipeline([('impute',SimpleImputer(strategy=cfg.model.numeric_imputation)),('scale',StandardScaler())])
    category = Pipeline([('impute',SimpleImputer(strategy=cfg.model.categorical_imputation)),('encode',OneHotEncoder(handle_unknown=cfg.model.unknown_categories,sparse_output=False))])
    transform = ColumnTransformer([('numeric',numeric,cfg.features.numeric),('categorical',category,cfg.features.categorical)])
    model = Ridge(alpha=cfg.model.alpha) if cfg.model.kind=='ridge' else DummyRegressor(strategy=cfg.model.dummy_strategy)
    return Pipeline([('preprocessing',transform),('model',model)])

def metrics(y,p): return {'mae':float(mean_absolute_error(y,p)), 'rmse':float(root_mean_squared_error(y,p))}

class Run:
    def __init__(self, cfg, directory): self.cfg=cfg; self.directory=Path(directory)
    @classmethod
    def create(cls, config='config.yaml', input_path=None):
        cfg=load(config); run_id=uuid.uuid4().hex
        directory=Path(cfg.paths.state)/'runs'/run_id; directory.mkdir(parents=True)
        write_json(directory/'config.json',cfg.model_dump())
        source=code_snapshot()
        write_json(directory/'source.json',source)
        for name in source['files']:
            dest=directory/'source'/name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(name,dest)
        client,eid=setup_tracking(cfg)
        tracked=client.create_run(eid,tags={'code.sha256':source['sha256'],'code.commit':source['commit'],'local.run_id':run_id})
        write_json(directory/'run.json',{'id':run_id,'created':now(),'input':str(Path(input_path or cfg.paths.training).resolve()),'mlflow_run_id':tracked.info.run_id,'stages':{},'status':'CREATED'})
        client.log_dict(tracked.info.run_id,cfg.model_dump(),'configuration.json')
        client.log_dict(tracked.info.run_id,source,'source.json')
        client.log_artifacts(tracked.info.run_id,str(directory/'source'),'source')
        return cls(cfg,directory)
    @classmethod
    def open(cls, directory):
        directory=Path(directory); return cls(Config.model_validate(read_json(directory/'config.json')),directory)
    @property
    def meta(self): return read_json(self.directory/'run.json')
    def stage(self,name):
        if name not in STAGES: raise ValueError('Unknown stage')
        meta=self.meta
        for dep in DEPENDENCIES[name]:
            if meta['stages'].get(dep,{}).get('status')!='PASSED': raise GateError(f'{name} requires successful {dep}')
        for prior in STAGES[:STAGES.index(name)]:
            for filename, expected_hash in meta['stages'].get(prior,{}).get('artifacts',{}).items():
                if not (self.directory/filename).exists() or digest(self.directory/filename)!=expected_hash:
                    raise GateError(f'Upstream artifact changed: {filename}; rerun its producer')
        # Re-running producers after promotion risks mutating deployed artifacts.
        if meta.get('deployed') and name!='monitor': raise GateError('Deployed run is immutable; start a new run')
        # Invalidate descendants before rerun; never allow stale gate results.
        for downstream in STAGES[STAGES.index(name)+1:]: meta['stages'].pop(downstream,None)
        start=time.perf_counter()
        client,_=setup_tracking(self.cfg)
        try:
            result=getattr(self,name)()
            entry={'status':'PASSED','at':now(),'seconds':time.perf_counter()-start,'result':result,'artifacts':{f:digest(self.directory/f) for f in ARTIFACTS[name]}}
        except Exception as exc:
            entry={'status':'FAILED','at':now(),'seconds':time.perf_counter()-start,'error':str(exc)}
            meta['stages'][name]=entry; meta['status']='FAILED'
            write_json(self.directory/'run.json',meta)
            client.log_dict(meta['mlflow_run_id'],entry,f'stages/{name}.json')
            client.set_terminated(meta['mlflow_run_id'],'FAILED')
            raise
        meta['stages'][name]=entry; meta['status']='RUNNING'
        if name=='deploy': meta['deployed']=True
        if name=='monitor': meta['status']='FINISHED'
        write_json(self.directory/'run.json',meta)
        client.log_dict(meta['mlflow_run_id'],entry,f'stages/{name}.json')
        if name=='monitor': client.set_terminated(meta['mlflow_run_id'],'FINISHED')
        print(json.dumps({'run':meta['id'],'stage':name,**entry}),flush=True)
        return result
    def ingest(self):
        source=Path(self.meta['input']); target=self.directory/'raw.csv'
        shutil.copyfile(source,target)
        manifest={'source':str(source),'sha256':digest(target),'bytes':target.stat().st_size}
        write_json(self.directory/'data.json',manifest)
        client,_=setup_tracking(self.cfg); client.set_tag(self.meta['mlflow_run_id'],'data.sha256',manifest['sha256'])
        client.log_dict(self.meta['mlflow_run_id'],manifest,'data.json')
        return manifest
    def validate(self):
        if digest(self.directory/'raw.csv')!=read_json(self.directory/'data.json')['sha256']: raise GateError('Data snapshot hash mismatch')
        return validate_frame(pd.read_csv(self.directory/'raw.csv'),self.cfg)
    def features(self):
        df=pd.read_csv(self.directory/'raw.csv')
        dev,test=train_test_split(df.index,test_size=self.cfg.split.test,random_state=self.cfg.seed)
        train,val=train_test_split(dev,test_size=self.cfg.split.validation/(1-self.cfg.split.test),random_state=self.cfg.seed)
        for label,idx in [('train',train),('validation',val),('test',test)]: df.loc[idx].to_csv(self.directory/f'{label}.csv',index=False)
        return {'train':len(train),'validation':len(val),'test_reserved':len(test),'features':self.cfg.features.all}
    def train(self):
        df=pd.read_csv(self.directory/'train.csv'); model=estimator(self.cfg)
        model.fit(df[self.cfg.features.all],df[self.cfg.features.target]); joblib.dump(model,self.directory/'model.joblib')
        return {'model_kind':self.cfg.model.kind,'sha256':digest(self.directory/'model.joblib')}
    def evaluate(self):
        cfg=self.cfg; df=pd.read_csv(self.directory/'validation.csv'); model=joblib.load(self.directory/'model.joblib')
        scores=metrics(df[cfg.features.target],model.predict(df[cfg.features.all]))
        errors=[]
        if scores['mae']>cfg.quality.max_mae or scores['rmse']>cfg.quality.max_rmse: errors.append('Candidate exceeds absolute error thresholds')
        champion=production(cfg)
        if champion:
            old=joblib.load(champion['model_path']); baseline=metrics(df[cfg.features.target],old.predict(df[cfg.features.all])); scores['champion_mae']=baseline['mae']
            if scores['mae']>baseline['mae']*(1+cfg.quality.max_relative_regression): errors.append('Candidate regresses against current production')
        result={'metrics':scores,'passed':not errors,'errors':errors,'champion_version':champion['version'] if champion else None,'model_sha256':digest(self.directory/'model.joblib')}
        write_json(self.directory/'evaluation.json',result)
        client,_=setup_tracking(cfg)
        for k,v in scores.items(): client.log_metric(self.meta['mlflow_run_id'],k,v)
        client.log_dict(self.meta['mlflow_run_id'],result,'evaluation.json')
        if errors: raise GateError('; '.join(errors))
        return result
    def register(self):
        evaluation=read_json(self.directory/'evaluation.json')
        if not evaluation['passed'] or digest(self.directory/'model.joblib')!=evaluation['model_sha256']: raise GateError('Model or gate changed after evaluation')
        cfg=self.cfg; client,_=setup_tracking(cfg)
        model=joblib.load(self.directory/'model.joblib'); example=pd.read_csv(self.directory/'train.csv')[cfg.features.all].head(2)
        with mlflow.start_run(run_id=self.meta['mlflow_run_id']):
            info=mlflow.sklearn.log_model(model,name='model',input_example=example,signature=mlflow.models.infer_signature(example,model.predict(example)),registered_model_name=cfg.tracking.registered_model)
        versions=client.search_model_versions(f"name='{cfg.tracking.registered_model}'")
        version=next(v for v in versions if v.run_id==self.meta['mlflow_run_id'])
        client.set_model_version_tag(cfg.tracking.registered_model,version.version,'lifecycle','validated')
        result={'version':version.version,'model_uri':info.model_uri,'mlflow_run_id':self.meta['mlflow_run_id']}
        write_json(self.directory/'registration.json',result); return result
    def deploy(self):
        cfg=self.cfg; client,_=setup_tracking(cfg)
        with deployment_lock(cfg):
            old=production(cfg); evaluation=read_json(self.directory/'evaluation.json')
            if (old['version'] if old else None)!=evaluation['champion_version']: raise GateError('Production changed; re-evaluate candidate in a new run')
            if digest(self.directory/'model.joblib')!=evaluation['model_sha256']: raise GateError('Model changed after evaluation')
            reg=read_json(self.directory/'registration.json'); model=joblib.load(self.directory/'model.joblib')
            sample=pd.read_csv(self.directory/'validation.csv')[cfg.features.all].head(1)
            if not np.isfinite(model.predict(sample)).all(): raise GateError('Prediction smoke check failed')
            # Copy into immutable release storage, then atomically switch the serving pointer.
            release=Path(cfg.paths.state).resolve()/'releases'/str(reg['version']); release.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(self.directory/'model.joblib',release/'model.joblib')
            manifest={**reg,'model_path':str(release/'model.joblib'),'model_sha256':digest(release/'model.joblib'),
                      'run_directory':str(self.directory.resolve()),'source':read_json(self.directory/'source.json'),
                      'data':read_json(self.directory/'data.json'),'configuration':cfg.model_dump(),'validation':evaluation['metrics'],'deployed_at':now()}
            write_json(release/'manifest.json',manifest)
            # Alias is a registry label; production.json is the serving source of truth.
            client.set_registered_model_alias(cfg.tracking.registered_model,'champion',reg['version'])
            try:
                if old: write_json(Path(cfg.paths.state)/'previous.json',old)
                write_json(Path(cfg.paths.state)/'production.json',manifest)
            except Exception:
                if old: client.set_registered_model_alias(cfg.tracking.registered_model,'champion',old['version'])
                else: client.delete_registered_model_alias(cfg.tracking.registered_model,'champion')
                raise
            client.set_model_version_tag(cfg.tracking.registered_model,reg['version'],'lifecycle','production')
            if old and old['version']!=reg['version']: client.set_model_version_tag(cfg.tracking.registered_model,old['version'],'lifecycle','archived')
            return {'version':reg['version'],'previous':old['version'] if old else None,'prediction_check':'passed'}
    def monitor(self):
        from .monitoring import monitor
        result=monitor(self.cfg)
        write_json(self.directory/'monitoring.json',result)
        return result

def pipeline(config='config.yaml', input_path=None, stop_after=None):
    run=Run.create(config,input_path)
    for stage in STAGES:
        run.stage(stage)
        if stage==stop_after:
            meta=run.meta; meta['status']='PARTIAL'; write_json(run.directory/'run.json',meta)
            client,_=setup_tracking(run.cfg); client.set_tag(meta['mlflow_run_id'],'pipeline.outcome','stopped_after_'+stage)
            client.set_terminated(meta['mlflow_run_id'],'FINISHED')
            break
    return run

def rollback(cfg):
    with deployment_lock(cfg):
        previous=read_json(Path(cfg.paths.state)/'previous.json'); current=production(cfg)
        if digest(previous['model_path'])!=previous['model_sha256']: raise GateError('Rollback artifact hash mismatch')
        joblib.load(previous['model_path'])
        client,_=setup_tracking(cfg)
        client.set_registered_model_alias(cfg.tracking.registered_model,'champion',previous['version'])
        try:
            write_json(Path(cfg.paths.state)/'production.json',previous)
        except Exception:
            client.set_registered_model_alias(cfg.tracking.registered_model,'champion',current['version'])
            raise
        write_json(Path(cfg.paths.state)/'previous.json',current)
        client.set_model_version_tag(cfg.tracking.registered_model,previous['version'],'lifecycle','production')
        client.set_model_version_tag(cfg.tracking.registered_model,current['version'],'lifecycle','archived')
        result={'at':now(),'from':current['version'],'to':previous['version'],'status':'PASSED'}
        write_json(Path(cfg.paths.reports)/'rollback.json',result); return result
