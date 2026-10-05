import argparse
import json
from pathlib import Path
from .config import load
from .core import Run, STAGES, pipeline, production, rollback, metrics, write_json

def main():
    p=argparse.ArgumentParser(); p.add_argument('--config',default='config.yaml')
    sub=p.add_subparsers(dest='command',required=True)
    run=sub.add_parser('run'); run.add_argument('--input'); run.add_argument('--stop-after',choices=STAGES)
    stage=sub.add_parser('stage'); stage.add_argument('name',choices=STAGES); stage.add_argument('--run',required=True)
    for name in ['lineage','rollback','monitor','serve','final-test','demo']: sub.add_parser(name)
    args=p.parse_args(); cfg=load(args.config)
    if args.command=='run': print('RUN_DIRECTORY='+str(pipeline(args.config,args.input,args.stop_after).directory))
    elif args.command=='stage': Run.open(args.run).stage(args.name)
    elif args.command=='lineage': print(json.dumps(production(cfg),indent=2))
    elif args.command=='rollback': print(json.dumps(rollback(cfg),indent=2))
    elif args.command=='monitor':
        from .monitoring import monitor
        print(json.dumps(monitor(cfg),indent=2))
    elif args.command=='serve':
        import uvicorn
        from .api import create_app
        uvicorn.run(create_app(args.config),host=cfg.serving.host,port=cfg.serving.port)
    elif args.command=='demo':
        from .demo import demonstrate
        demonstrate(args.config)
    elif args.command=='final-test':
        import joblib
        import pandas as pd
        current=production(cfg)
        if not current: raise ValueError('Deploy a validated candidate first')
        output=Path(cfg.paths.reports)/'final_test.json'
        if output.exists(): raise ValueError('Final evaluation already recorded; preserve the result rather than repeatedly selecting on test')
        df=pd.read_csv(Path(current['run_directory'])/'test.csv')
        model=joblib.load(current['model_path'])
        result={'model_version':current['version'],'rows':len(df),'purpose':'One-time final historical test; not used for selection',**metrics(df[cfg.features.target],model.predict(df[cfg.features.all]))}
        write_json(output,result); print(json.dumps(result,indent=2))

if __name__=='__main__': main()
