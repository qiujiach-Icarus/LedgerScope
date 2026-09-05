import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd

from src.ledger.application.services import LedgerService
from src.pattern.application.services import PatternService
from src.anomaly.application.services import AnomalyService
from src.reporting.application.services import ReportingService

# 界面主题配置
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class AuditApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("离线财务凭证多维离群审计排查系统 (Air-Gapped Edition)")
        self.geometry("1100x750")

        self.selected_file = None
        self.df_result = None
        self.tracer = None

        self._build_ui()

    def _build_ui(self):
        # 顶部控制栏
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=15, pady=10)

        self.btn_select = ctk.CTkButton(top_frame, text="📁 选择待排查 Excel 账本", command=self._select_file)
        self.btn_select.pack(side="left", padx=10, pady=10)

        self.lbl_file = ctk.CTkLabel(top_frame, text="未选择文件", text_color="gray")
        self.lbl_file.pack(side="left", padx=10)

        self.btn_run = ctk.CTkButton(top_frame, text="🚀 启动白盒检测", command=self._run_audit_thread, state="disabled")
        self.btn_run.pack(side="right", padx=10, pady=10)

        self.save_db_var = ctk.BooleanVar(value=True)
        self.chk_save_db = ctk.CTkCheckBox(top_frame, text="存入数据库", variable=self.save_db_var)
        self.chk_save_db.pack(side="right", padx=10)

        self.btn_export = ctk.CTkButton(top_frame, text="📥 导出审计底稿", command=self._export_excel, state="disabled")
        self.btn_export.pack(side="right", padx=10)

        # 中间参数与状态区
        param_frame = ctk.CTkFrame(self)
        param_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(param_frame, text="离群敏感度 (Contamination):").pack(side="left", padx=10)
        self.slider_contam = ctk.CTkSlider(param_frame, from_=0.01, to=0.10, number_of_steps=9)
        self.slider_contam.set(0.03)
        self.slider_contam.pack(side="left", padx=10)

        self.lbl_status = ctk.CTkLabel(param_frame, text="状态: 就绪", text_color="green")
        self.lbl_status.pack(side="right", padx=15)

        # 主内容分栏区 (左边看依赖链日志，右边看高危单据)
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # 左侧：数学依赖链与内部拓扑日志
        left_box = ctk.CTkFrame(main_frame, width=420)
        left_box.pack(side="left", fill="both", padx=5, pady=5)
        ctk.CTkLabel(left_box, text="🔬 数学计算依赖链 (Audit Trail)", font=("Arial", 14, "bold")).pack(pady=5)

        self.txt_log = ctk.CTkTextbox(left_box, wrap="word")
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=5)

        # 右侧：排查结果穿透清单
        right_box = ctk.CTkFrame(main_frame)
        right_box.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(right_box, text="📌 重点高危可疑单据清单 (Top Anomalies)", font=("Arial", 14, "bold")).pack(pady=5)

        self.txt_results = ctk.CTkTextbox(right_box, wrap="none", font=("Courier", 12))
        self.txt_results.pack(fill="both", expand=True, padx=5, pady=5)

    def _select_file(self):
        f = filedialog.askopenfilename(filetypes=[("Excel 文件", "*.xlsx *.xls")])
        if f:
            self.selected_file = f
            self.lbl_file.configure(text=os.path.basename(f), text_color="black")
            self.btn_run.configure(state="normal")

    def _run_audit_thread(self):
        self.btn_run.configure(state="disabled")
        self.lbl_status.configure(text="状态: 正在多维拓扑切分中...", text_color="orange")
        threading.Thread(target=self._run_audit, daemon=True).start()

    def _run_audit(self):
        try:
            # 1. 预处理 (LedgerService)
            ledger_service = LedgerService()
            save_to_db = self.save_db_var.get()
            df_clean, info = ledger_service.process_excel(self.selected_file, save_to_db=save_to_db)

            # 2. 统计中继 (PatternService)
            self.pattern_service = PatternService(alpha=0.7)
            df_featured = self.pattern_service.analyze_patterns(df_clean)

            # 3. 孤立森林拓扑 (AnomalyService)
            contam = round(self.slider_contam.get(), 2)
            features = ["amount", "month", "day_of_week", "direction_code", "amount_deviation_ratio"]
            anomaly_service = AnomalyService(contamination=contam, n_estimators=100)
            self.df_result = anomaly_service.detect_anomalies(df_featured, feature_cols=features)

            # 4. 渲染依赖链日志
            log_text = "【阶段 1：特征维度来源绑定】\n"
            for k, v in info["meta_trace"].items():
                log_text += f"• {k}\n  ↳ {v}\n"

            log_text += "\n【阶段 2：全局先验与平滑】\n"
            for k, v in self.pattern_service.get_summary().items():
                log_text += f"• {k}: {v}\n"

            log_text += "\n【阶段 3：孤立森林拓扑参数】\n"
            for k, v in anomaly_service.tree_trace.items():
                log_text += f"• {k}: {v}\n"

            self.txt_log.delete("1.0", "end")
            self.txt_log.insert("1.0", log_text)

            # 5. 渲染高危凭证列表
            top10 = self.df_result.head(10)
            res_text = f"{'凭证号':<8} | {'金额':<12} | {'偏离度':<8} | {'树深度':<7} | {'评分':<6} | 摘要\n"
            res_text += "=" * 80 + "\n"
            for _, r in top10.iterrows():
                res_text += f"{str(r['voucher_id']):<8} | ¥{r['amount']:<11,.2f} | {r['偏离倍数']:<6}倍 | {r['平均切分深度']:<5}刀 | {r['风险评分']:<6} | {r['摘要']}\n"

            self.txt_results.delete("1.0", "end")
            self.txt_results.insert("1.0", res_text)

            self.lbl_status.configure(text="状态: 排查完成", text_color="green")
            self.btn_export.configure(state="normal")
            self.btn_run.configure(state="normal")

        except Exception as e:
            messagebox.showerror("运行异常", f"排查中断: {str(e)}")
            self.lbl_status.configure(text="状态: 出错", text_color="red")
            self.btn_run.configure(state="normal")

    def _export_excel(self):
        if self.df_result is None:
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel 工作簿", "*.xlsx")])
        if save_path:
            reporting_service = ReportingService()
            reporting_service.generate_audit_report(self.df_result, self.pattern_service.acc_stats, save_path)
            messagebox.showinfo("成功", "双 Sheet 审计底稿已成功导出！")


if __name__ == "__main__":
    app = AuditApp()
    app.mainloop()