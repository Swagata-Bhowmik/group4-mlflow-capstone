"""Distribution and labeled-performance monitoring; no automatic unsafe promotion."""
import html
from pathlib import Path
import joblib
import pandas as pd
from scipy.stats import ks_2samp
from .core import production, metrics, validate_frame, write_json, read_json, now


def monitor(cfg):
    deployed=production(cfg)
    if not deployed: raise ValueError('No production model')
    model=joblib.load(deployed['model_path'])
    # Immutable source snapshot of the deployed model, not a potentially edited input file.
    reference=pd.read_csv(Path(deployed['run_directory'])/'train.csv')
    incoming=pd.read_csv(cfg.paths.incoming)
    if set(incoming.Batch.unique())!={1,2,3}: raise ValueError('Expected batches 1, 2, 3')
    reports=[]
    for batch, df in incoming.groupby('Batch',sort=True):
        df=df.drop(columns='Batch'); validate_frame(df,cfg)
        scores=metrics(df[cfg.features.target],model.predict(df[cfg.features.all]))
        shifts={}
        for col in cfg.features.numeric:
            shifts[col]={'method':'KS D', 'value':float(ks_2samp(reference[col].dropna(),df[col].dropna()).statistic), 'threshold':cfg.monitoring.ks_threshold}
        for col in cfg.features.categorical:
            a=reference[col].value_counts(normalize=True); b=df[col].value_counts(normalize=True); idx=a.index.union(b.index)
            shifts[col]={'method':'total variation','value':float((a.reindex(idx,fill_value=0)-b.reindex(idx,fill_value=0)).abs().sum()/2),'threshold':cfg.monitoring.categorical_tv_threshold}
        drifted=[c for c,s in shifts.items() if s['value']>s['threshold']]
        missing={c:float(abs(df[c].isna().mean()-reference[c].isna().mean())) for c in cfg.features.all}
        missing_alert=[c for c,v in missing.items() if v>cfg.monitoring.max_missing_delta]
        ratio=scores['mae']/max(deployed['validation']['mae'],1e-12)
        performance=scores['mae']>cfg.monitoring.max_mae or ratio>cfg.monitoring.max_mae_ratio
        reports.append({'batch':int(batch),'rows':len(df),'model_version':deployed['version'],**scores,'mae_ratio':ratio,'feature_statistics':shifts,
                        'drifted_features':drifted,'missingness_deltas':missing,'missingness_alerts':missing_alert,'data_alert':bool(drifted or missing_alert),'performance_alert':performance,
                        'action':'Investigate; enqueue retraining candidate through all gates; retain current model' if drifted or missing_alert or performance else 'Continue serving and monitoring'})
    result={'created':now(),'reference':'Training partition of deployed model','reference_rows':len(reference),'model_version':deployed['version'],
            'policy':'Effect-size thresholds; not significance tests. Input changes alone do not prove performance degradation.', 'batches':reports}
    write_json(Path(cfg.paths.reports)/'monitoring.json',result)
    write_json(Path(deployed['run_directory'])/'monitoring.json',result)
    render_report(cfg,result)
    return result


def render_report(cfg,result):
    cards=''
    for b in result['batches']:
        alert=b['data_alert'] or b['performance_alert']
        cards+=f'''<article><span class="badge {'warn' if alert else 'ok'}">{'INVESTIGATE' if alert else 'STABLE'}</span><h2>Batch {b['batch']}</h2><p class="number">₹{b['mae']:.2f}<small> lakhs MAE</small></p><p>RMSE ₹{b['rmse']:.2f} lakhs · error ratio {b['mae_ratio']:.2f}×</p><p>Input shift: {html.escape(', '.join(b['drifted_features']) or 'none above threshold')}</p><p>Performance alert: {'yes' if b['performance_alert'] else 'no'}</p><p>{html.escape(b['action'])}</p></article>'''
    operations=''
    operational_path=Path(cfg.paths.reports)/'operational.json'
    if operational_path.exists():
        op=read_json(operational_path)
        operations=f"<h2>Measured API operations</h2><p>{op['requests']} warm sequential requests · p95 {op['p95_seconds']*1000:.2f} ms · errors {op['errors']}. Method: {html.escape(op['transport'])}. This is not a container/network load test.</p>"
    page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Group 4 · Monitoring evidence</title><style>body{{font:16px/1.6 system-ui;background:#101b2c;color:#edf3fc;margin:0;padding:5vw}}main{{max-width:1150px;margin:auto}}h1{{font-size:clamp(28px,4vw,48px);line-height:1.15}}.eyebrow{{color:#75d8cc;letter-spacing:.12em}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:20px}}article{{background:#1b2b43;border:1px solid #39516e;border-radius:16px;padding:24px}}.number{{font-size:38px;margin:12px 0}}small{{font-size:16px}}.badge{{font-size:12px;padding:5px 10px;border-radius:6px}}.ok{{background:#16564e}}.warn{{background:#734720}}footer{{color:#b8c7da;margin-top:30px}}a{{color:#75d8cc}}</style><main><p class="eyebrow">GROUP 4 / MEASURED EVIDENCE</p><h1>Prices change.<br>Our monitoring shows where.</h1><p>House-price model v{result['model_version']} · reference: {result['reference_rows']:,} training listings · 500 labeled listings per batch</p><div class="grid">{cards}</div>{operations}<footer><p>Data alerts: numeric KS D &gt; {cfg.monitoring.ks_threshold}; categorical total variation &gt; {cfg.monitoring.categorical_tv_threshold}. Performance alert: MAE &gt; ₹{cfg.monitoring.max_mae} lakhs or &gt; {cfg.monitoring.max_mae_ratio}× validation MAE.</p><p>Alerts trigger investigation, never automatic promotion. Data shift and model error are reported separately. This report contains measured batch results; API operational measurements are in operational.json.</p><p>Generated {result['created']} · <a href="monitoring.json">Full numerical evidence</a></p></footer></main></html>'''
    path=Path(cfg.paths.reports)/'monitoring.html'; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(page, encoding='utf-8')
