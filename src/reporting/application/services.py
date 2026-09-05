import pandas as pd
from ..infrastructure.excel import ExcelReporter

class ReportingService:
    def __init__(self):
        self.excel_reporter = ExcelReporter()

    def generate_audit_report(self, df_result: pd.DataFrame, acc_stats: pd.DataFrame, output_path: str):
        return self.excel_reporter.export(df_result, acc_stats, output_path)
