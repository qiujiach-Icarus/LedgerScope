import pandas as pd
import os

class ExcelReporter:
    def __init__(self):
        self.output_cols = [
            "voucher_id", "date", "account", "direction", "amount",
            "科目历史均值", "平滑参考基准", "偏离倍数", "平均切分深度",
            "风险评分", "是否异常", "异常原因诊断", "摘要"
        ]

    def export(self, df_result: pd.DataFrame, acc_stats: pd.DataFrame, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            cols_to_save = [c for c in self.output_cols if c in df_result.columns]
            df_result[cols_to_save].to_excel(
                writer, sheet_name="异常排查清单", index=False
            )
            acc_stats.to_excel(
                writer, sheet_name="中间科目统计底稿", index=False
            )
        return output_path
