"""Reproducible historical-data experiment; never evaluates the reserved test set."""

import argparse
import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    args = parser.parse_args()
    config_bytes = args.config.read_bytes()
    cfg = yaml.safe_load(config_bytes)
    seed = cfg['random_seed']
    test_fraction = cfg['test_fraction']
    validation_fraction = cfg['validation_fraction']
    if not (0 < test_fraction < 1 and 0 < validation_fraction < 1 - test_fraction):
        raise ValueError('Test and validation fractions must leave a nonempty training set.')
    if cfg['selection_metric'] != 'mae':
        raise ValueError('This initial experiment supports validation MAE selection only.')

    data_path = Path(cfg['data_path'])
    before_hash = hashlib.sha256(data_path.read_bytes()).hexdigest()
    data = pd.read_csv(data_path)
    numeric = cfg['numeric_features']
    categorical = cfg['categorical_features']
    features = numeric + categorical
    if len(set(features)) != len(features) or set(features) & {cfg['target'], cfg['id_column'], 'Batch'}:
        raise ValueError('Feature list must be unique and exclude the target and identifiers.')
    required = features + [cfg['id_column'], cfg['target']]
    if not set(required).issubset(data.columns):
        raise ValueError('Required input columns are missing.')
    if data[cfg['id_column']].isna().any() or data[cfg['id_column']].duplicated().any():
        raise ValueError('Listing IDs must be present and unique.')
    if not np.isfinite(data[cfg['target']]).all():
        raise ValueError('Target values must be present and finite.')

    development, test_idx = train_test_split(
        data.index.to_numpy(), test_size=test_fraction, random_state=seed
    )
    train_idx, validation_idx = train_test_split(
        development, test_size=validation_fraction / (1 - test_fraction), random_state=seed
    )
    partitions = {'train': train_idx, 'validation': validation_idx, 'test_reserved': test_idx}
    if sum(len(set(v)) for v in partitions.values()) != len(data) or len(set().union(*map(set, partitions.values()))) != len(data):
        raise RuntimeError('Partitions must be disjoint and cover every source row.')

    out = Path(cfg['output_dir'])
    out.mkdir(parents=True, exist_ok=True)
    membership = pd.concat([
        pd.DataFrame({'House_ID': data.loc[idx, cfg['id_column']].to_numpy(), 'partition': name})
        for name, idx in partitions.items()
    ])
    membership.to_csv(out / 'split_membership.csv', index=False)
    x_train, y_train = data.loc[train_idx, features], data.loc[train_idx, cfg['target']]
    x_val, y_val = data.loc[validation_idx, features], data.loc[validation_idx, cfg['target']]
    pp = cfg['preprocessing']
    constructors = {
        'dummy_median': lambda params: DummyRegressor(**params),
        'ridge': lambda params: Ridge(**params),
        'random_forest': lambda params: RandomForestRegressor(random_state=seed, **params),
        'histogram_gradient_boosting': lambda params: HistGradientBoostingRegressor(
            random_state=seed, early_stopping=False, **params
        ),
    }
    rows = []
    predictions = pd.DataFrame({
        'House_ID': data.loc[validation_idx, cfg['id_column']].to_numpy(),
        'actual_price_lakhs': y_val.to_numpy(),
    })
    fitted = {}
    for name, params in cfg['models'].items():
        preprocessing = ColumnTransformer([
            ('numeric', Pipeline([
                ('imputer', SimpleImputer(strategy=pp['numeric_imputation'])),
                ('scale', StandardScaler()),
            ]), numeric),
            ('categorical', Pipeline([
                ('imputer', SimpleImputer(strategy=pp['categorical_imputation'])),
                ('encode', OneHotEncoder(handle_unknown=pp['unknown_categories'], sparse_output=False)),
            ]), categorical),
        ])
        model = Pipeline([('preprocess', preprocessing), ('regressor', constructors[name](params))])
        start = perf_counter()
        model.fit(x_train, y_train)
        duration = perf_counter() - start
        predicted = model.predict(x_val)
        train_predicted = model.predict(x_train)
        row = {
            'model': name,
            'validation_mae_lakhs': float(mean_absolute_error(y_val, predicted)),
            'validation_rmse_lakhs': float(root_mean_squared_error(y_val, predicted)),
            'validation_r2': float(r2_score(y_val, predicted)),
            'training_mae_lakhs': float(mean_absolute_error(y_train, train_predicted)),
            'fit_seconds': duration,
        }
        rows.append(row)
        predictions[name] = predicted
        fitted[name] = model
        print(json.dumps(row), flush=True)

    rows.sort(key=lambda r: r['validation_mae_lakhs'])
    selected = rows[0]['model']
    predictions.to_csv(out / 'validation_predictions.csv', index=False)
    joblib.dump(fitted[selected], out / 'selected_model.joblib')
    after_hash = hashlib.sha256(data_path.read_bytes()).hexdigest()
    if before_hash != after_hash:
        raise RuntimeError('Source data changed during the experiment.')
    result = {
        'purpose': 'Initial validation comparison, not final test performance or production release',
        'configuration': cfg,
        'configuration_sha256': hashlib.sha256(config_bytes).hexdigest(),
        'source_sha256': before_hash,
        'source_unchanged': before_hash == after_hash,
        'partition_rows': {k: len(v) for k, v in partitions.items()},
        'test_evaluated': False,
        'incoming_batches_loaded': False,
        'selected_on': 'lowest validation MAE',
        'selected_model': selected,
        'results': rows,
        'environment': {'python': platform.python_version(), **{
            name: version(name) for name in ['pandas', 'numpy', 'scipy', 'scikit-learn', 'PyYAML', 'joblib']
        }},
    }
    (out / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Selected:', selected, '| Test set reserved; incoming batches not loaded.', flush=True)


if __name__ == '__main__':
    main()
