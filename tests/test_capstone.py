import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import yaml
from fastapi.testclient import TestClient
from capstone.config import load
from capstone.core import GateError, Run, pipeline, production, validate_frame, digest
from capstone.api import create_app

@pytest.fixture
def cfg_path(tmp_path):
    c=yaml.safe_load(Path('config.yaml').read_text())
    c['paths']['state']=str(tmp_path/'state'); c['paths']['reports']=str(tmp_path/'reports')
    p=tmp_path/'config.yaml';p.write_text(yaml.safe_dump(c));return p

def test_configuration_rejects_invalid_split(cfg_path):
    c=yaml.safe_load(cfg_path.read_text());c['split']['validation']=.9;cfg_path.write_text(yaml.safe_dump(c))
    with pytest.raises(ValueError):load(cfg_path)

def test_configuration_rejects_feature_leakage(cfg_path):
    c=yaml.safe_load(cfg_path.read_text());c['features']['numeric'].append('Price_Lakhs');cfg_path.write_text(yaml.safe_dump(c))
    with pytest.raises(ValueError):load(cfg_path)

@pytest.mark.parametrize('change',['missing','category','infinity','duplicate','fractional','extra'])
def test_bad_data_rejected(cfg_path,change):
    cfg=load(cfg_path);df=pd.read_csv(cfg.paths.training)
    if change=='missing':df.loc[:800,'Age_Years']=np.nan
    if change=='category':df.loc[0,'City_Zone']='Moon'
    if change=='infinity':df.loc[0,'Price_Lakhs']=np.inf
    if change=='duplicate':df.loc[1,'House_ID']=df.loc[0,'House_ID']
    if change=='fractional':df.loc[0,'Age_Years']=1.5
    if change=='extra':df['target_copy']=df.Price_Lakhs
    with pytest.raises(GateError):validate_frame(df,cfg)

def test_rerun_invalidates_descendants_and_requires_dependencies(cfg_path):
    run=Run.create(cfg_path)
    with pytest.raises(GateError):run.stage('train')
    for stage in ['ingest','validate','features','train','evaluate']:run.stage(stage)
    original=run.meta['stages']['evaluate']['result']['metrics']['mae']
    run.stage('train')
    assert 'evaluate' not in run.meta['stages']
    with pytest.raises(GateError):run.stage('register')
    run.stage('evaluate')
    assert abs(run.meta['stages']['evaluate']['result']['metrics']['mae']-original)<run.cfg.quality.reproducibility_tolerance

def test_split_preprocessing_and_baseline_reproduction(cfg_path):
    run=pipeline(cfg_path,stop_after='evaluate')
    a,b,c=[pd.read_csv(run.directory/f'{p}.csv') for p in ['train','validation','test']]
    assert [len(a),len(b),len(c)]==[2400,800,800]
    ids=[set(x.House_ID) for x in [a,b,c]]
    assert not ids[0]&ids[1] and not ids[0]&ids[2] and not ids[1]&ids[2]
    import joblib
    model=joblib.load(run.directory/'model.joblib')
    imputer=model.named_steps['preprocessing'].named_transformers_['numeric'].named_steps['impute']
    assert np.allclose(imputer.statistics_,a[run.cfg.features.numeric].median().values)
    assert abs(run.meta['stages']['evaluate']['result']['metrics']['mae']-5.741987567526319)<run.cfg.quality.reproducibility_tolerance

def test_model_gate_failure_has_no_production(cfg_path):
    c=yaml.safe_load(cfg_path.read_text());c['model']['kind']='dummy';cfg_path.write_text(yaml.safe_dump(c))
    with pytest.raises(GateError):pipeline(cfg_path)
    assert production(load(cfg_path)) is None

def test_no_model_api_returns_503(cfg_path):
    client=TestClient(create_app(cfg_path));assert client.get('/health').status_code==503

def test_full_safe_failure_and_rollback_demo(cfg_path):
    from capstone.demo import demonstrate
    demonstrate(cfg_path)
    cfg=load(cfg_path)
    report=json.loads((Path(cfg.paths.reports)/'safe_failures.json').read_text())
    assert all(s['production_manifest_unchanged'] for s in report['scenarios'])
    assert json.loads((Path(cfg.paths.reports)/'rollback.json').read_text())['status']=='PASSED'
    client=TestClient(create_app(cfg_path))
    assert client.get('/health').status_code==200
    assert 'prediction_requests_total' in client.get('/metrics').text
    manifest=production(cfg);run=Run.open(manifest['run_directory'])
    with pytest.raises(GateError):run.stage('train')

def test_modified_upstream_artifact_is_rejected(cfg_path):
    run=pipeline(cfg_path,stop_after='features')
    path=run.directory/'train.csv'
    path.write_text(path.read_text()+'\n')
    with pytest.raises(GateError,match='Upstream artifact changed'):run.stage('train')

def test_champion_comparison_can_reject_despite_absolute_pass(cfg_path):
    from capstone.core import write_json
    import joblib
    # Same model evaluated on same rows, with a deliberately shifted incumbent
    # intercept to create a small measurable MAE advantage for this isolated test.
    run=pipeline(cfg_path,stop_after='train')
    model=joblib.load(run.directory/'model.joblib')
    df=pd.read_csv(run.directory/'validation.csv')
    residual=df[run.cfg.features.target]-model.predict(df[run.cfg.features.all])
    model.named_steps['model'].intercept_ += float(residual.median())
    champion=run.directory/'champion.joblib';joblib.dump(model,champion)
    write_json(Path(run.cfg.paths.state)/'production.json',{'version':'test-incumbent','model_path':str(champion)})
    run.cfg.quality.max_relative_regression=0
    with pytest.raises(GateError,match='regresses'):run.stage('evaluate')
    evidence=json.loads((run.directory/'evaluation.json').read_text())
    assert evidence['metrics']['mae']<run.cfg.quality.max_mae
