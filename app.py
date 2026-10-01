import json
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 頁面配置
st.set_page_config(
    page_title="Jailbreak & Safety Classifier Showcase",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ LLM Safety & Jailbreak Classifier Showcase")
st.markdown(
    "本介面展示 AI 安全防護分類器之診斷結果、倫理原則判定、類別機率分佈與 SHAP 特徵歸因分析。"
)


# 載入資料
@st.cache_data
def load_data():
    with open("showcase_data.json", "r", encoding="utf-8") as f:
        return json.load(f)


try:
    data = load_data()
except Exception as e:
    st.error(f"無法載入 showcase_data.json，請確認檔案格式是否正確: {e}")
    st.stop()

# 側邊欄：選擇樣本
st.sidebar.header("🎯 測試範例選擇")
sample_ids = [f"{item['id']} ({item['Harmfulness']})" for item in data]
selected_option = st.sidebar.selectbox("請選擇測試範例 (Sample ID):", sample_ids)

# 取得目前選中的數據
selected_index = sample_ids.index(selected_option)
item = data[selected_index]

# --- 頂部區塊：安全倫理指標 ---
st.markdown("---")
top_col1, top_col2, top_col3 = st.columns([2, 1.5, 1])

with top_col1:
    st.subheader(f"📌 {item['id']}")
    st.markdown(f"**Safety Principle:** `{item['Principle']}`")

with top_col2:
    # 根據 Harmfulness 給予不同顏色的 Badge 提示
    harm_level = item.get("Harmfulness", "")
    if "Level 0" in harm_level or "Harmless" in harm_level:
        st.success(f"🛡️ **Harmfulness:** {harm_level}")
    elif "Level 1" in harm_level or "Moderate" in harm_level:
        st.warning(f"⚠️ **Harmfulness:** {harm_level}")
    else:
        st.error(f"🚨 **Harmfulness:** {harm_level}")

with top_col3:
    status = (
        "✅ Match"
        if item["prediction"] == item["ground_truth"]
        else "❌ Misclassified"
    )
    st.metric(
        label="Pred / Ground Truth",
        value=f"{item['prediction']}",
        delta=f"GT: {item['ground_truth']} ({status})",
    )

# --- 區塊 1：輸入提示詞 (Input Prompt) ---
st.markdown("### 💬 Evaluated Input Prompt")
st.info(f"“ {item['input_prompt']} ”")

st.markdown("---")

# --- 區塊 2：類別機率分佈與 SHAP 雙欄分析 ---
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.markdown("### 📊 Classification Probabilities")

    probs = item["probabilities"]
    labels = list(probs.keys())
    values = list(probs.values())

    # 自訂三分類安全配色 (Benign: 綠, Harmful: 橘/黃, Jailbreak: 紅)
    color_map = {
        "Benign": "#2ecc71",
        "Harmful": "#f39c12",
        "Jailbreak": "#e74c3c",
    }
    colors = [color_map.get(lbl, "#3498db") for lbl in labels]

    fig_prob = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker_color=colors,
            text=[f"{v:.1f}%" for v in values],
            textposition="auto",
        )
    )

    fig_prob.update_layout(
        xaxis_title="Predicted Class",
        yaxis_title="Probability (%)",
        yaxis=dict(range=[0, 105]),
        height=360,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig_prob, use_container_width=True)

with col_right:
    st.markdown("### 🧬 SHAP Feature Attribution")

    shap_data = item["shap_values"]
    features = [f"{s['feature']}" for s in shap_data]
    shap_vals = [s["shap_value"] for s in shap_data]

    # 正值代表推向越危險/越強的判定(紅)，負值代表拉回安全(藍)
    shap_colors = ["#e74c3c" if v >= 0 else "#3498db" for v in shap_vals]

    fig_shap = go.Figure(
        go.Bar(
            x=shap_vals,
            y=features,
            orientation="h",
            marker_color=shap_colors,
            text=[f"{v:+.3f}" for v in shap_vals],
            textposition="auto",
        )
    )

    fig_shap.update_layout(
        xaxis_title="SHAP Value (Contribution to Model Output)",
        yaxis_title="Features / Concepts",
        yaxis=dict(autorange="reversed"),
        height=360,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig_shap, use_container_width=True)

# --- 區塊 3：診斷說明 ---
st.markdown("### 💡 Model Diagnosis & Notes")
st.markdown(f"> {item.get('analysis_notes', '無額外說明。')}")
