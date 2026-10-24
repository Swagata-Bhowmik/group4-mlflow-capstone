import hashlib
from pathlib import Path
from typing import Literal
import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', serialize_by_alias=True)

class Paths(Strict):
    training: str
    incoming: str
    state: str
    reports: str

class Split(Strict):
    test: float = Field(gt=0, lt=1)
    validation: float = Field(gt=0, lt=1)
    @model_validator(mode='after')
    def fractions(self):
        if self.test + self.validation >= 1: raise ValueError('Split leaves no training rows')
        return self

class Features(Strict):
    numeric: list[str]
    categorical: list[str]
    target: str
    identifier: str
    @property
    def all(self): return self.numeric + self.categorical
    @model_validator(mode='after')
    def safe(self):
        if len(set(self.all)) != len(self.all) or set(self.all) & {self.target, self.identifier, 'Batch'}:
            raise ValueError('Duplicate features or target/identifier leakage')
        return self

class Schema(Strict):
    missing_allowed: list[str]
    max_missing_fraction: float = Field(ge=0, lt=1)
    min_rows: int = Field(gt=0)
    ranges: dict[str, tuple[float, float]]
    integers: list[str]
    categories: dict[str, list[str]]
    @model_validator(mode='after')
    def bounds(self):
        if any(lo >= hi for lo, hi in self.ranges.values()): raise ValueError('Invalid range')
        return self

class Model(Strict):
    kind: Literal['ridge', 'dummy']
    alpha: float = Field(gt=0)
    numeric_imputation: Literal['median', 'mean']
    categorical_imputation: Literal['most_frequent']
    unknown_categories: Literal['ignore', 'error']
    dummy_strategy: Literal['median', 'mean']

class Quality(Strict):
    max_mae: float = Field(gt=0)
    max_rmse: float = Field(gt=0)
    max_relative_regression: float = Field(ge=0, le=0.1)
    reproducibility_tolerance: float = Field(gt=0)

class Tracking(Strict):
    experiment: str
    registered_model: str

class Monitoring(Strict):
    ks_threshold: float = Field(gt=0, lt=1)
    categorical_tv_threshold: float = Field(gt=0, lt=1)
    max_mae: float = Field(gt=0)
    max_mae_ratio: float = Field(gt=1)
    max_missing_delta: float = Field(ge=0, lt=1)
    max_model_age_days: int = Field(gt=0)
    p95_latency_seconds: float = Field(gt=0)
    max_error_rate: float = Field(ge=0, lt=1)
    benchmark_requests: int = Field(gt=0)
    prediction_buckets: list[float]
    latency_buckets: list[float]

class Serving(Strict):
    host: str
    port: int = Field(gt=0, lt=65536)
    max_batch_size: int = Field(gt=0)

class Config(Strict):
    project: str
    paths: Paths
    seed: int
    split: Split
    features: Features
    data_schema: Schema = Field(alias="schema")
    model: Model
    quality: Quality
    tracking: Tracking
    monitoring: Monitoring
    serving: Serving
    @model_validator(mode='after')
    def columns(self):
        if set(self.data_schema.ranges) != set(self.features.numeric + [self.features.target]):
            raise ValueError('Every numeric feature and target must have a range')
        if set(self.data_schema.categories) != set(self.features.categorical):
            raise ValueError('Every categorical feature must have allowed categories')
        if not set(self.data_schema.missing_allowed) <= set(self.features.all): raise ValueError('Invalid nullable column')
        if not set(self.data_schema.integers) <= set(self.features.numeric): raise ValueError('Invalid integer column')
        return self

def load(path='config.yaml'):
    return Config.model_validate(yaml.safe_load(Path(path).read_text(encoding='utf-8')))

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
