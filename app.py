import json
import plotly.graph_objects as go
import streamlit as st

# 頁面配置
st.set_page_config(
    page_title="LLM Safety Classifier Showcase",
    page_icon="🛡️",
    layout="wide",
)

# 自訂 CSS 樣式：美化 Prompt 卡片、標籤與間距
st.markdown(
    """
    <style>
    /* 核心 Prompt 卡片美化 */
    .prompt-box {
        background-color: #1e293b;
        border-left: 5px solid #3b82f6;
        padding: 20px 24px;
        border-radius: 8px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .prompt-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .prompt-text {
        color: #f8fafc;
        font-size: 1.25rem;
        font-weight: 500;
        line-height: 1.6;
    }
    
    /* 元數據標籤列 */
    .meta-container {
        display: flex;
        gap: 16px;
        align-items: center;
        margin-bottom: 28px;
        flex-wrap: wrap;
    }
    .meta-tag {
        background-color: #0f172a;
        border: 1px solid #334155;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.9rem;
        color: #cbd5e1;
    }
    .meta-tag strong {
        color: #38bdf8;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 載入資料 (不加快取，確保即時讀取最新 JSON)
def load_data():
    with open("showcase_data.json", "r", encoding="utf-8") as f:
        return json.load(f)


try:
    data = load_data()
except Exception as e:
    st.error(f"無法載入 showcase_data.json: {e}")
    st.stop()

if not data or not isinstance(data, list):
    st.warning("showcase_data.json 為空或格式無效。")
    st.stop()

# 側邊欄：選擇樣本
st.sidebar.title("🛡️ Classifier Showcase")
st.sidebar.markdown("---")
sample_ids = [
    f"{item.get('id', 'Unknown_ID')} | {item.get('Harmfulness', 'N/A')}"
    for item in data
]
selected_option = st.sidebar.selectbox("🎯 選擇測試範例 (Sample):", sample_ids)

# 取得目前選中的數據
selected_index = sample_ids.index(selected_option)
item = data[selected_index]

# 安全提取欄位值
item_id = item.get("id", "N/A")
principle = item.get("Principle", "N/A")
harm_level = item.get("Harmfulness", "N/A")
prediction = item.get("prediction", "N/A")
ground_truth = item.get("ground_truth", "N/A")
input_prompt = item.get("input_prompt", "無提示詞內容")
analysis_notes = item.get("analysis_notes", "無額外分析說明。")

# ==========================================
# 1. 重點視覺：巨型顯眼的 Input Prompt 卡片
# ==========================================
st.markdown(
    f"""
    <div class="prompt-box">
        <div class="prompt-title">💬 Evaluated Input Prompt ({item_id})</div>
        <div class="prompt-text">“ {input_prompt} ”</div>
    </div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. 輔助資訊：Principle & Harmfulness 標籤列
# ==========================================
st.markdown(
    f"""
    <div class="meta-container">
        <div class="meta-tag">📋 <strong>Principle:</strong> {principle}</div>
        <div class="meta-tag">⚠️ <strong>Harmfulness:</strong> {harm_level}</div>
    </div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")

# ==========================================
# 3. 核心雙欄分析區 (左：Pred + 瘦橫向直方圖 | 右：SHAP)
# ==========================================
col_left, col_right = st.columns([1, 1.1], gap="large")

with col_left:
    # 3.1 大字體 Pred / GT 判定結果
    status_icon = "✅" if prediction == ground_truth else "❌"
    st.markdown(f"##### 🎯 Prediction Result")
    st.markdown(
        f"<h2 style='color: #ef4444; margin-top: -10px; margin-bottom: 0px;'>{prediction}</h2>",
        unsafe_allow_html=True,
    )
    st.caption(
        f"Ground Truth: **{ground_truth}** ({status_icon} Match) | Confidence: **{item.get('confidence', 0):.2f}%**"
    )

    st.markdown("---")

    # 3.2 三種分類機率（橫向 Left-to-Right 瘦柱狀圖）
    st.markdown("##### 📊 Class Probabilities")
    probs = item.get("probabilities", {})

    if probs and isinstance(probs, dict):
        labels = list(probs.keys())
        values = list(probs.values())

        # 語意配色 (Benign: 綠, Harmful: 黃/橘, Jailbreak: 紅)
        color_map = {
            "Benign": "#22c55e",
            "Harmful": "#eab308",
            "Jailbreak": "#ef4444",
        }
        colors = [color_map.get(lbl, "#3b82f6") for lbl in labels]

        # 橫向 (Left-to-Right) 條形圖，設定 width 使柱體較瘦且細緻
        fig_prob = go.Figure(
            go.Bar(
                x=values,
                y=labels,
                orientation="h",
                marker_color=colors,
                width=0.35,  # 調整柱子粗細 (瘦柱體)
                text=[f"{v:.1f}%" if v > 1 else f"{v:.2f}" for v in values],
                textposition="outside",
            )
        )

        fig_prob.update_layout(
            xaxis_title="Probability (%)",
            yaxis=dict(autorange="reversed"),  # 依序列出
            height=260,
            margin=dict(l=10, r=40, t=10, b=30),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_prob, use_container_width=True)

with col_right:
    # 3.3 SHAP 特徵歸因分析
    st.markdown("##### 🧬 SHAP Feature Attribution")
    shap_data = item.get("shap_values", [])

    if shap_data and isinstance(shap_data, list):
        features = [s.get("feature", "Unk") for s in shap_data]
        shap_vals = [s.get("shap_value", 0.0) for s in shap_data]

        # 正值推向危險(紅)，負值拉回安全(藍)
        shap_colors = ["#ef4444" if v >= 0 else "#3b82f6" for v in shap_vals]

        fig_shap = go.Figure(
            go.Bar(
                x=shap_vals,
                y=features,
                orientation="h",
                marker_color=shap_colors,
                width=0.35,  # 瘦柱體
                text=[f"{v:+.3f}" for v in shap_vals],
                textposition="outside",
            )
        )

        fig_shap.update_layout(
            xaxis_title="SHAP Value (Impact on Model)",
            yaxis=dict(autorange="reversed"),
            height=360,
            margin=dict(l=10, r=40, t=10, b=30),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_shap, use_container_width=True)

# ==========================================
# 4. 診斷說明卡片
# ==========================================
st.markdown("---")
st.markdown("##### 💡 Model Diagnosis & Notes")
st.info(analysis_notes)
