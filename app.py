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
    initial_sidebar_state="expanded"
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
# 2. 資料載入 (對接 showcase_data.json)
# -----------------------------------------------------------------------------
def load_showcase_data(file_path="showcase_data.json"):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

dataset = load_showcase_data()

if not dataset:
    st.error("⚠️ 未偵測到 showcase_data.json，請確保檔案放在專案根目錄。")
    st.stop()

# 若 JSON 內有多筆資料，可以在側邊欄選取 ID
sample_ids = [item.get("id", f"Sample_{idx}") for idx, item in enumerate(dataset)]
selected_id = st.sidebar.selectbox("🔍 Select Evaluation Sample", sample_ids)

# 取得當前選取的資料物件
selected_item = next((item for item in dataset if item.get("id") == selected_id), dataset[0])

# 提取資料欄位
prompt_id = selected_item.get("id", "N/A")
principle = selected_item.get("Principle", "N/A")
harmfulness_level = selected_item.get("Harmfulness", "N/A")
input_prompt = selected_item.get("input_prompt", "")

ground_truth = selected_item.get("ground_truth", "N/A")
prediction_result = selected_item.get("prediction", "N/A")
confidence = float(selected_item.get("confidence", 0.0))

prob_data = selected_item.get("probabilities", {})
shap_list = selected_item.get("shap_values", [])

# -----------------------------------------------------------------------------
# 3. 頂部 Evaluated Input Prompt 區塊
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="prompt-box">
    <div class="prompt-title">💬 EVALUATED INPUT PROMPT ({prompt_id})</div>
    <div class="prompt-text">“ {input_prompt} ”</div>
    <div class="badge-container">
        <div class="badge badge-blue">📋 Principle: {principle}</div>
        <div class="badge badge-orange">⚠️ Harmfulness: {harmfulness_level}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. 主畫面雙欄布局
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([1, 1.1], gap="large")

with col_left:
    st.markdown("### 🎯 Prediction Result")
    
    # 根據預測結果決定顏色
    is_malicious = str(prediction_result).lower() in ["malicious", "jailbreak", "harmful"]
    status_class = "status-malicious" if is_malicious else "status-benign"
    st.markdown(f'<div class="{status_class}">{prediction_result}</div>', unsafe_allow_html=True)
    
    # 比對 Ground Truth 與 Prediction 是否一致
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
        x_max_prob = max(max_prob * 1.25, 100) # 預留右側 25% 緩衝區防裁切

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
    
    if shap_list:
        # 解析 shap_values 陣列 [{"feature": ..., "shap_value": ...}]
        raw_features = [str(item.get("feature", "")) for item in shap_list]
        values = [float(item.get("shap_value", 0.0)) for item in shap_list]
        shap_colors = ["#f85149" if v > 0 else "#58a6ff" for v in values]

        # 1. 依據最長特徵名稱長度，動態調整左側 Margin (最少 140px，最多 320px)
        max_feat_len = max([len(f) for f in raw_features]) if raw_features else 10
        dynamic_left_margin = min(max(max_feat_len * 8, 140), 320)

        # 2. 特徵名稱截斷處理 (超過 32 字元顯示 ...)
        def truncate_label(label, max_len=32):
            return label if len(label) <= max_len else label[:max_len-3] + "..."

        display_features = [truncate_label(f) for f in raw_features]

        # 3. 計算動態 X 軸極限，防止右側與左側數據溢出
        min_val = min(values) if values and min(values) < 0 else 0
        max_val = max(values) if values and max(values) > 0 else 0
        x_min = min_val * 1.45 if min_val < 0 else -0.15
        x_max = max_val * 1.45 if max_val > 0 else 0.15

        # 4. 防壓字關鍵：正數置外 (outside)，負數置內 (inside)，絕對不撞 Y 軸特徵名
        text_positions = ["outside" if v >= 0 else "inside" for v in values]

        fig_shap = go.Figure()
        fig_shap.add_trace(go.Bar(
            x=values,
            y=display_features,
            orientation='h',
            marker=dict(color=shap_colors),
            text=[f"{v:+.3f}" for v in values],
            textposition=text_positions,
            hovertext=raw_features, # 滑鼠懸停時顯示完整特徵全名
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
