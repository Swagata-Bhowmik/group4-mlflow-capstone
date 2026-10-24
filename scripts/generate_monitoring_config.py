"""Generate dashboard and alert thresholds from the single YAML configuration."""
import json
from pathlib import Path
import yaml
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run from any folder, no PYTHONPATH needed
from capstone.config import load
cfg=load()
rules=[
 {'alert':'HighPredictionLatency','expr':f'histogram_quantile(0.95, sum(rate(prediction_latency_seconds_bucket[5m])) by (le)) > {cfg.monitoring.p95_latency_seconds}','for':'2m','labels':{'severity':'warning'},'annotations':{'summary':'Investigate prediction latency; retain the serving model'}},
 {'alert':'PredictionErrors','expr':f'sum(rate(prediction_requests_total{{status!="200"}}[5m])) / clamp_min(sum(rate(prediction_requests_total[5m])), 0.000001) > {cfg.monitoring.max_error_rate}','for':'2m','labels':{'severity':'warning'},'annotations':{'summary':'Inspect invalid requests and serving errors'}},
 {'alert':'ModelStale','expr':f'model_age_days > {cfg.monitoring.max_model_age_days}','for':'5m','labels':{'severity':'warning'},'annotations':{'summary':'Schedule a candidate run; require all gates before promotion'}},
 {'alert':'ModelReloadFailed','expr':'increase(model_reload_failures_total[5m]) > 0','labels':{'severity':'critical'},'annotations':{'summary':'Candidate reload failed; inspect artifacts and rollback through pipeline'}},
 {'alert':'APIUnavailable','expr':'up{job="house-price-api"} == 0','for':'1m','labels':{'severity':'critical'},'annotations':{'summary':'Restore API or roll back container release'}}]
Path('monitoring/alerts.yml').write_text(yaml.safe_dump({'groups':[{'name':'capstone','rules':rules}]},sort_keys=False), encoding='utf-8')
queries=[('p95 latency (seconds)','histogram_quantile(0.95, sum(rate(prediction_latency_seconds_bucket[5m])) by (le))'),('Throughput (requests / second)','sum(rate(prediction_requests_total[5m]))'),('Error fraction','sum(rate(prediction_requests_total{status!="200"}[5m])) / clamp_min(sum(rate(prediction_requests_total[5m])), 0.000001)'),('Mean predicted price (lakhs)','rate(predicted_price_lakhs_sum[5m]) / clamp_min(rate(predicted_price_lakhs_count[5m]), 0.000001)'),('Predicted-price cumulative distribution','sum(rate(predicted_price_lakhs_bucket[5m])) by (le)'),('Model age (days)','model_age_days')]
panels=[]
for i,(title,q) in enumerate(queries):
 panels.append({'id':i+1,'title':title,'type':'timeseries','datasource':{'type':'prometheus','uid':'prometheus'},'gridPos':{'x':(i%2)*12,'y':(i//2)*8,'w':12,'h':8},'targets':[{'expr':q,'refId':'A'}]})
Path('monitoring/dashboard.json').write_text(json.dumps({'uid':'group4-capstone','title':'Group 4 · House-price operations','schemaVersion':39,'version':1,'refresh':'5s','time':{'from':'now-15m','to':'now'},'panels':panels},indent=2)+'\n', encoding='utf-8')
