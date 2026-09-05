import os
import pandas as pd
from src.ledger.application.services import LedgerService
from src.pattern.application.services import PatternService
from src.anomaly.application.services import AnomalyService
from src.reporting.application.services import ReportingService

def main():
    input_excel = os.path.join("data", "raw", "test_data.xlsx")
    output_excel = os.path.join("data", "output", "透明审计工作底稿.xlsx")

    # =========================================================================
    # 阶段 1：数据清洗与维度映射 (LedgerService)
    # =========================================================================
    ledger_service = LedgerService()
    # 开启数据库存储：save_to_db=True
    df_clean, prep_info = ledger_service.process_excel(input_excel, save_to_db=True)

    # =========================================================================
    # 阶段 2：独立统计量处理与偏离度计算 (PatternService)
    # =========================================================================
    pattern_service = PatternService(alpha=0.7)
    df_featured = pattern_service.analyze_patterns(df_clean)

    # =========================================================================
    # 阶段 3：孤立森林白盒检测与拓扑追踪 (AnomalyService)
    # =========================================================================
    target_features = ["amount", "month", "day_of_week", "direction_code", "amount_deviation_ratio"]
    anomaly_service = AnomalyService(contamination=0.03, n_estimators=100)
    df_result = anomaly_service.detect_anomalies(df_featured, feature_cols=target_features)

    # =========================================================================
    # 阶段 4：白盒因果依赖链控制台展示
    # =========================================================================
    print("\n" + "=" * 95)
    print(" 🛡️ 智能财务凭证离群审计系统 - 白盒数学依赖链追踪 (New Architecture)")
    print("=" * 95)

    print("\n【阶段 1：Excel 字段 ➔ 数学维度绑定记录】")
    for dim, desc in prep_info["meta_trace"].items():
        print(f"  • {dim:<30} ➔ {desc}")

    print("\n【阶段 2：统计基准与收缩平滑】")
    for k, v in pattern_service.get_summary().items():
        print(f"  • {k}: {v}")

    print("\n【阶段 3：孤立森林内部拓扑日志】")
    for k, v in anomaly_service.tree_trace.items():
        print(f"  • {k}: {v}")

    print("\n【阶段 4：高危风险单据凭证链 (Top 5 穿透)】")
    print("-" * 95)
    for idx, (_, r) in enumerate(df_result.head(5).iterrows(), 1):
        v_id = r["voucher_id"]
        d_str = str(r["date"])[:10]
        amt = r["amount"]
        acc_m = r["科目历史均值"]
        sm_m = r["平滑参考基准"]
        ratio = r["偏离倍数"]
        depth = r["平均切分深度"]
        score = r["风险评分"]
        desc = r["摘要"]
        acc = r["account"]
        diag = r["异常原因诊断"]

        print(f"【证据链 No.{idx}】凭证: {v_id} | 记账日期: {d_str} | 综合评分: {score} 分")
        print(f"  ▶ 业务摘要: {desc} ({acc})")
        print(f"  ▶ 资金敞口: ¥{amt:,.2f} | 科目均值: ¥{acc_m:,.2f} | 先验平滑基准: ¥{sm_m:,.2f}")
        print(f"  ▶ 结构偏离: {ratio:.2f} 倍基准 | 异常诊断: {diag}")
        print(f"  ▶ 空间拓扑: iTree 平均切分 {depth:.2f} 刀即可完全孤立 (正常基准约 {anomaly_service.tree_trace['全样本平均隔离深度基准']} 刀)")
        print("-" * 95)

    # =========================================================================
    # 阶段 5：导出审计工作底稿 (ReportingService)
    # =========================================================================
    reporting_service = ReportingService()
    reporting_service.generate_audit_report(df_result, pattern_service.acc_stats, output_excel)

    print(f"\n[*] 包含各阶段数学验证结果的双 Sheet 底稿已生成: {output_excel}\n")

if __name__ == "__main__":
    main()