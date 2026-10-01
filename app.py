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

if not data or not isinstance(data, list):
    st.warning("showcase_data.json 為空或格式無效 (應為 JSON 陣列)。")
    st.stop()

# 側邊欄：選擇樣本 (使用 .get 安全取得欄位，避免 KeyError)
st.sidebar.header("🎯 測試範例選擇")
sample_ids = [
    f"{item.get('id', 'Unknown_ID')} ({item.get('Harmfulness', 'N/A')})"
    for item in data
]
selected_option = st.sidebar.selectbox("請選擇測試範例 (Sample ID):", sample_ids)

# 取得目前選中的數據
selected_index = sample_ids.index(selected_option)
item = data[selected_index]

# 安全提取欄位值並給予預設預防機制
item_id = item.get("id", "N/A")
principle = item.get("Principle", "N/A")
harm_level = item.get("Harmfulness", "N/A")
prediction = item.get("prediction", "N/A")
ground_truth = item.get("ground_truth", "N/A")
input_prompt = item.get("input_prompt", "無提示詞內容")
analysis_notes = item.get("analysis_notes", "無額外分析說明。")

# --- 頂部區塊：安全倫理指標 ---
st.markdown("---")
top_col1, top_col2, top_col3 = st.columns([2, 1.5, 1])

with top_col1:
    st.subheader(f"📌 {item_id}")
    st.markdown(f"**Safety Principle:** `{principle}`")

with top_col2:
    if "Level 0" in harm_level or "Harmless" in harm_level:
        st.success(f"🛡️ **Harmfulness:** {harm_level}")
    elif "Level 1" in harm_level or "Moderate" in harm_level:
        st.warning(f"⚠️ **Harmfulness:** {harm_level}")
    else:
        st.error(f"🚨 **Harmfulness:** {harm_level}")

with top_col3:
    status = (
        "✅ Match"
        if (prediction == ground_truth and prediction != "N/A")
        else "❌ Misclassified"
    )
    st.metric(
        label="Pred / Ground Truth",
        value=f"{prediction}",
        delta=f"GT: {ground_truth} ({status})",
    )

# --- 區塊 1：輸入提示詞 (Input Prompt) ---
st.markdown("### 💬 Evaluated Input Prompt")
st.info(f"“ {input_prompt} ”")

st.markdown("---")

# --- 區塊 2：類別機率分佈與 SHAP 雙欄分析 ---
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.markdown("### 📊 Classification Probabilities")
    probs = item.get("probabilities", {})

    if probs and isinstance(probs, dict):
        labels = list(probs.keys())
        values = list(probs.values())

        # 自訂三分類安全配色
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
                text=[f"{v:.1f}%" if v > 1 else f"{v:.2f}" for v in values],
                textposition="auto",
            )
        )

        fig_prob.update_layout(
            xaxis_title="Predicted Class",
            yaxis_title="Probability (%)",
            yaxis=dict(range=[0, max(values) * 1.15 if values else 100]),
            height=360,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig_prob, use_container_width=True)
    else:
        st.write("尚無機率數據。")

with col_right:
    st.markdown("### 🧬 SHAP Feature Attribution")
    shap_data = item.get("shap_values", [])

    if shap_data and isinstance(shap_data, list):
        features = [s.get("feature", "Unk") for s in shap_data]
        shap_vals = [s.get("shap_value", 0.0) for s in shap_data]

        # 正值代表推向危險/Jailbreak判定(紅)，負值代表拉回安全(藍)
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
    else:
        st.write("尚無 SHAP 特徵資料。")

# --- 區塊 3：診斷說明 ---
st.markdown("### 💡 Model Diagnosis & Notes")
st.markdown(f"> {analysis_notes}")
