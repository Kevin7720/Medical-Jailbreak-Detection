import json
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 頁面配置
st.set_page_config(
    page_title="Classifier Evaluation Showcase",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Classifier Prediction & SHAP Explanation Showcase")
st.markdown("本頁面展示預先計算好的模型診斷結果、類別機率與 SHAP 特徵歸因分析。")


# 載入預先準備好的結果資料
@st.cache_data
def load_data():
    with open("showcase_data.json", "r", encoding="utf-8") as f:
        return json.load(f)


data = load_data()

# 側邊欄：選擇樣本
st.sidebar.header("🎯 樣本選擇區")
sample_titles = [item["title"] for item in data]
selected_title = st.sidebar.selectbox("請選擇測試範例 (Sample Input):", sample_titles)

# 取得目前選中的數據
selected_sample = next(item for item in data if item["title"] == selected_title)

# --- 主要內容區 ---
st.subheader(f"📌 {selected_sample['title']}")
st.caption(f"Category: `{selected_sample['category']}`")

# 區塊 1: 原始輸入與預測摘要
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ground Truth", selected_sample["ground_truth"])
col2.metric("Prediction", selected_sample["prediction"])
col3.metric("Confidence", f"{selected_sample['confidence'] * 100:.1f}%")
status = (
    "✅ Correct"
    if selected_sample["prediction"] == selected_sample["ground_truth"]
    else "❌ Misclassified"
)
col4.metric("Status", status)

st.markdown("---")

# 區塊 2: 雙欄排版 (左：類別機率 / 右：SHAP 特徵貢獻)
left_col, right_col = st.columns([1, 1.5])

with left_col:
    st.markdown("### 📊 Prediction Probabilities")
    probs = selected_sample["probabilities"]

    fig_prob = px.bar(
        x=list(probs.keys()),
        y=list(probs.values()),
        labels={"x": "Class", "y": "Probability"},
        range_y=[0, 1],
        color=list(probs.keys()),
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_prob.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig_prob, use_container_width=True)

    with st.expander("📝 原始輸入內容 (Input Summary)"):
        st.code(selected_sample["input_summary"], language="text")

with right_col:
    st.markdown("### 🧬 SHAP Feature Contribution")

    shap_data = selected_sample["shap_values"]
    features = [f"{item['feature']} ({item['value']})" for item in shap_data]
    shap_vals = [item["shap_value"] for item in shap_data]

    # 設定正負顏色的 SHAP 條形圖
    colors = ["#EF553B" if v >= 0 else "#636EFA" for v in shap_vals]

    fig_shap = go.Figure(
        go.Bar(
            x=shap_vals,
            y=features,
            orientation="h",
            marker_color=colors,
            text=[f"{v:+.3f}" for v in shap_vals],
            textposition="auto",
        )
    )

    fig_shap.update_layout(
        xaxis_title="SHAP Value (Impact on Model Output)",
        yaxis_title="Feature (Value)",
        yaxis=dict(autorange="reversed"),
        height=350,
        margin=dict(l=20, r=20, t=30, b=30),
    )
    st.plotly_chart(fig_shap, use_container_width=True)

# 區塊 3: 診斷說明與分析註記
st.markdown("### 💡 Model Diagnosis & Notes")
st.info(selected_sample["analysis_notes"])