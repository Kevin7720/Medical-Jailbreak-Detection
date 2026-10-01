import streamlit as st
import plotly.graph_objects as go
import json
import os

# -----------------------------------------------------------------------------
# 1. 頁面配置與全域黑夜模式 CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LLM Safety & Jailbreak Detection",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .prompt-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 24px;
    }
    .prompt-title {
        font-size: 12px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .prompt-text {
        font-size: 17px;
        font-weight: 500;
        color: #f0f6fc;
        margin-bottom: 14px;
        line-height: 1.5;
    }
    .badge-container {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 13px;
        font-weight: 500;
        background-color: #21262d;
        border: 1px solid #30363d;
    }
    .badge-blue { color: #58a6ff; border-color: #1f6beb; }
    .badge-orange { color: #f0883e; border-color: #bd561d; }
    .badge-green { color: #3fb950; background-color: rgba(46, 160, 67, 0.15); border-color: #2ea043; }
    .badge-red { color: #f85149; background-color: rgba(248, 81, 73, 0.15); border-color: #f85149; }
    
    .status-malicious {
        color: #f85149;
        font-size: 32px;
        font-weight: 700;
        margin-top: 4px;
    }
    .status-benign {
        color: #3fb950;
        font-size: 32px;
        font-weight: 700;
        margin-top: 4px;
    }
    .ground-truth-row {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        font-size: 14px;
        color: #8b949e;
        margin-top: 6px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 資料載入函數 (直接對接外部 JSON/Data Pipeline)
# -----------------------------------------------------------------------------
def load_evaluation_data(data_path="eval_results.json"):
    """
    從 JSON 或資料來源讀取真實評估數據。
    如果檔案不存在，會從 st.session_state 或是外部傳入的 dict 讀取。
    """
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # 如果尚未建立檔案，預設從 session_state 取用或丟出提示
        return st.session_state.get("eval_data", None)

# 從資料源取得 payload
data = load_evaluation_data()

# 當完全沒有資料傳入時的防護畫面
if not data:
    st.error("⚠️ 未偵測到評估資料 (eval_results.json)。請確保推論結果已寫入資料集或傳入 data 物件。")
    st.stop()

# 解析真實資料欄位
prompt_id = data.get("prompt_id", "EVAL_PROMPT_01")
input_prompt = data.get("input_prompt", "")
principle = data.get("principle", "N/A")
harmfulness_level = data.get("harmfulness_level", "N/A")

prediction_result = data.get("prediction_result", "Unknown")
ground_truth = data.get("ground_truth", "Unknown")
confidence = data.get("confidence", 0.0)

# 類別機率字典 e.g., {"Benign": 0.58, "Harmful": 0.42, "Jailbreak": 90.09}
prob_data = data.get("class_probabilities", {})

# SHAP 特徵字典 e.g., {"Feature_Name": 0.45, ...}
shap_data = data.get("shap_values", {})

# -----------------------------------------------------------------------------
# 3. 頂部 Evaluated Input Prompt 區塊
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="prompt-box">
    <div class="prompt-title">💬 Evaluated Input Prompt ({prompt_id})</div>
    <div class="prompt-text">“ {input_prompt} ”</div>
    <div class="badge-container">
        <div class="badge badge-blue">📋 Principle: {principle}</div>
        <div class="badge badge-orange">⚠ Harmfulness: {harmfulness_level}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. 主畫面雙欄布局
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([1, 1.1], gap="large")

with col_left:
    st.markdown("### 🎯 Prediction Result")
    
    # 根據預測結果切換動態顏色
    status_class = "status-malicious" if prediction_result.lower() in ["malicious", "jailbreak", "harmful"] else "status-benign"
    st.markdown(f'<div class="{status_class}">{prediction_result}</div>', unsafe_allow_html=True)
    
    # 判斷 Ground Truth 與 Prediction 是否 Match
    is_match = str(prediction_result).strip().lower() == str(ground_truth).strip().lower()
    match_badge = '<span class="badge badge-green">✓ Match</span>' if is_match else '<span class="badge badge-red">✗ Mismatch</span>'

    st.markdown(f"""
    <div class="ground-truth-row">
        <span>Ground Truth: <strong style="color:#f0f6fc;">{ground_truth}</strong></span>
        {match_badge}
        <span>| Confidence: <strong style="color:#f0f6fc;">{confidence:.2f}%</strong></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📊 Class Probabilities")

    if prob_data:
        classes = list(prob_data.keys())
        probs = [float(v) for v in prob_data.values()]
        colors = ["#3fb950" if c.lower() == "benign" else "#d29922" if c.lower() == "harmful" else "#f85149" for c in classes]

        max_prob = max(probs) if probs else 100
        x_max_prob = max(max_prob * 1.2, 100) # 動態確保 % 標籤不被切割

        fig_prob = go.Figure()
        fig_prob.add_trace(go.Bar(
            x=probs,
            y=classes,
            orientation='h',
            marker=dict(color=colors),
            text=[f"{p:.2f}%" for p in probs],
            textposition='outside',
            cliponaxis=False
        ))

        fig_prob.update_layout(
            xaxis=dict(
                range=[0, x_max_prob],
                title="Probability (%)",
                showgrid=True,
                gridcolor="#21262d",
                zeroline=False
            ),
            yaxis=dict(autorange="reversed"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#c9d1d9"),
            margin=dict(l=10, r=60, t=10, b=40),
            height=300
        )
        st.plotly_chart(fig_prob, use_container_width=True)

with col_right:
    st.markdown("### 🧬 SHAP Feature Attribution")
    
    if shap_data:
        raw_features = list(shap_data.keys())
        values = [float(v) for v in shap_data.values()]
        shap_colors = ["#f85149" if v > 0 else "#58a6ff" for v in values]

        # 1. 根據真實資料中最長名稱動態計算左側邊距 (Left Margin)
        max_feat_len = max([len(str(f)) for f in raw_features]) if raw_features else 10
        dynamic_left_margin = min(max(max_feat_len * 7, 140), 320) # 彈性邊界 140px ~ 320px

        # 2. 名稱超長時做截斷，懸停顯示完整名稱
        def truncate_label(label, max_len=32):
            label_str = str(label)
            return label_str if len(label_str) <= max_len else label_str[:max_len-3] + "..."

        display_features = [truncate_label(f) for f in raw_features]

        # 3. 計算動態 X 軸，防數據溢出
        min_val = min(values) if values and min(values) < 0 else 0
        max_val = max(values) if values and max(values) > 0 else 0
        x_min = min_val * 1.4 if min_val < 0 else -0.1
        x_max = max_val * 1.4 if max_val > 0 else 0.1

        # 4. 防壓字修復：正數置外 (outside)，負數置內 (inside) 避免退回 x=0 壓住 Y 軸文字
        text_positions = ["outside" if v >= 0 else "inside" for v in values]

        fig_shap = go.Figure()
        fig_shap.add_trace(go.Bar(
            x=values,
            y=display_features,
            orientation='h',
            marker=dict(color=shap_colors),
            text=[f"{v:+.3f}" for v in values],
            textposition=text_positions,
            hovertext=raw_features,
            hoverinfo="text+x",
            cliponaxis=False
        ))

        fig_shap.update_layout(
            xaxis=dict(
                range=[x_min, x_max],
                title="SHAP Value (Impact on Model)",
                showgrid=True,
                gridcolor="#21262d",
                zeroline=True,
                zerolinecolor="#8b949e",
                zerolinewidth=2
            ),
            yaxis=dict(
                autorange="reversed",
                tickfont=dict(size=12, color="#c9d1d9")
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#c9d1d9"),
            margin=dict(l=dynamic_left_margin, r=70, t=10, b=40),
            height=300
        )
        st.plotly_chart(fig_shap, use_container_width=True)
