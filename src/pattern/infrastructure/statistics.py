import pandas as pd

class PatternStatistics:
    def __init__(self, alpha: float = 0.7):
        self.alpha = alpha
        self.global_mean = 0.0
        self.acc_stats = pd.DataFrame()

    def calculate_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        self.global_mean = float(df["amount"].mean())
        
        self.acc_stats = df.groupby("account")["amount"].agg(
            科目样本量="count",
            科目历史均值="mean"
        ).reset_index()

        self.acc_stats["平滑参考基准"] = (
            self.acc_stats["科目历史均值"] * self.alpha + self.global_mean * (1.0 - self.alpha)
        )

        df = df.merge(self.acc_stats, on="account", how="left")
        
        df["amount_deviation_ratio"] = df["amount"] / df["平滑参考基准"].replace(0, 1)
        df["偏离倍数"] = df["amount_deviation_ratio"].round(2)
        df["科目历史均值"] = df["科目历史均值"].round(2)
        df["平滑参考基准"] = df["平滑参考基准"].round(2)

        return df

    def get_summary(self) -> dict:
        return {
            "全局先验均值 (mu_global)": round(self.global_mean, 2),
            "平滑权重配置": f"{int(self.alpha * 100)}% 局部经验 + {int((1 - self.alpha) * 100)}% 全局先验",
            "覆盖会计科目数": len(self.acc_stats)
        }
