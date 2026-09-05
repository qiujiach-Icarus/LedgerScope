import pandas as pd
from ..infrastructure.statistics import PatternStatistics

class PatternService:
    def __init__(self, alpha: float = 0.7):
        self.stats_engine = PatternStatistics(alpha=alpha)

    def analyze_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.stats_engine.calculate_stats(df)

    def get_summary(self) -> dict:
        return self.stats_engine.get_summary()

    @property
    def acc_stats(self):
        return self.stats_engine.acc_stats
