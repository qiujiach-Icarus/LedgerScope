import pandas as pd
from ..infrastructure.ml import AnomalyMLModel

class AnomalyService:
    def __init__(self, contamination: float = 0.03, n_estimators: int = 100):
        self.ml_engine = AnomalyMLModel(contamination=contamination, n_estimators=n_estimators)

    def detect_anomalies(self, df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
        return self.ml_engine.fit_predict(df, feature_cols)

    @property
    def tree_trace(self):
        return self.ml_engine.tree_trace
