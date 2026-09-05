```python
import streamlit as st
import pandas as pd
import io
from src.ledger.application.services import LedgerService
from src.pattern.application.services import PatternService
from src.anomaly.application.services import AnomalyService
from src.reporting.application.services import ReportingService

# --- Page Config ---
st.set_page_config(
    page_title="AI 财务审计系统",
    page_icon="🚀",
    layout="wide"
)

# --- State Management ---
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'df_result' not in st.session_state:
    st.session_state.df_result = None
if 'audit_trail' not in st.session_state:
    st.session_state.audit_trail = ""
if 'pattern_service' not in st.session_state:
    st.session_state.pattern_service = None

# --- Functions ---
def run_audit(uploaded_file, contamination):
    """
    Orchestrates the entire audit process.
    """
    try:
        st.session_state.analysis_done = False
        st.session_state.df_result = None
        st.session_state.audit_trail = ""

        # Use BytesIO to handle the uploaded file in memory
        file_buffer = io.BytesIO(uploaded_file.getvalue())

        with st.spinner('正在加载和清洗账本数据...'):
            # 1. Preprocessing (LedgerService)
            ledger_service = LedgerService()
            df_clean, info = ledger_service.process_excel(file_buffer, save_to_db=False) # save_to_db is False for Streamlit

        with st.spinner('正在计算统计特征和业务模式...'):
            # 2. Pattern Analysis (PatternService)
            pattern_service = PatternService(alpha=0.7)
            df_featured = pattern_service.analyze_patterns(df_clean)
            st.session_state.pattern_service = pattern_service # Save for reporting

        with st.spinner('正在运行多维异常检测模型...'):
            # 3. Anomaly Detection (AnomalyService)
            features = ["amount", "month", "day_of_week", "direction_code", "amount_deviation_ratio"]
            anomaly_service = AnomalyService(contamination=contamination, n_estimators=100)
            df_result = anomaly_service.detect_anomalies(df_featured, feature_cols=features)
            st.session_state.df_result = df_result

        # 4. Build Audit Trail Log
        log_text = "【阶段 1：特征维度来源绑定】\n"
        for k, v in info["meta_trace"].items():
            log_text += f"• {k}\n  ↳ {v}\n"
        log_text += "\n【阶段 2：全局先验与平滑】\n"
        for k, v in pattern_service.get_summary().items():
            log_text += f"• {k}: {v}\n"
        log_text += "\n【阶段 3：孤立森林拓扑参数】\n"
        for k, v in anomaly_service.tree_trace.items():
            log_text += f"• {k}: {v}\n"

        st.session_state.audit_trail = log_text
        st.session_state.analysis_done = True
        st.success("审计排查完成！")

    except Exception as e:
        st.error(f"分析过程中出现错误: {e}")
        st.session_state.analysis_done = False

# --- UI Layout ---
st.title("🚀 AI 财务审计与账本异常检测系统")
st.markdown("上传您的 Excel 总账或明细账，系统将利用机器学习模型自动筛选高风险交易，并生成可追溯的审计线索。")

# --- Sidebar for Controls ---
with st.sidebar:
    st.header("⚙️ 控制面板")

    uploaded_file = st.file_uploader(
        "1. 选择待排查 Excel 账本",
        type=["xlsx", "xls"],
        help="请上传包含总账或明细账的 Excel 文件。"
    )

    contamination = st.slider(
        "2. 离群点敏感度 (Contamination)",
        min_value=0.01,
        max_value=0.10,
        value=0.03,
        step=0.01,
        help="这个参数决定了模型将多少比例的交易视为'异常'。值越高，发现的异常越多，但也可能包含更多正常交易。"
    )

    run_button = st.button(
        "🚀 启动白盒检测",
        disabled=(not uploaded_file),
        type="primary",
        use_container_width=True
    )

# --- Main Content Area ---
if run_button:
    run_audit(uploaded_file, contamination)

if st.session_state.analysis_done:
    st.header("📈 分析结果")

    # --- Download Button ---
    reporting_service = ReportingService()
    output_excel = io.BytesIO()
    # This is a simplified call; in a real scenario, you might need more data passed here
    reporting_service.generate_audit_report(st.session_state.df_result, st.session_state.pattern_service.acc_stats, output_excel)
    output_excel.seek(0)

    st.download_button(
        label="📥 下载详细审计底稿 (Excel)",
        data=output_excel,
        file_name="audit_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔬 数学计算依赖链 (Audit Trail)")
        st.code(st.session_state.audit_trail, language="text")

    with col2:
        st.subheader("📌 重点高危可疑单据清单 (Top Anomalies)")
        if st.session_state.df_result is not None:
            # Display a more user-friendly table
            display_df = st.session_state.df_result[[
                'voucher_id', '摘要', 'amount', '风险评分', '偏离倍数', '平均切分深度'
            ]].copy()
            display_df.rename(columns={
                'voucher_id': '凭证号',
                'amount': '金额',
            }, inplace=True)
            st.dataframe(
                display_df.head(20),
                use_container_width=True,
                column_config={
                    "金额": st.column_config.NumberColumn(format="¥%.2f")
                }
            )
        else:
            st.warning("没有发现可疑单据。")
else:
    st.info("请在左侧上传文件并点击“启动白盒检测”开始分析。")

```
