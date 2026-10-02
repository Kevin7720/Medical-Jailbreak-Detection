import json
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

# 設定頁面配置
st.set_page_config(
    page_title="醫療文本有害性與 SHAP 可解釋性分析儀表板",
    page_icon="🩺",
    layout="wide",
)


# 1. 載入資料 (讀取 JSON)
@st.cache_data
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"無法讀取 data.json: {e}")
        return []


data = load_data()

# 標題區塊
st.title("🩺 醫療 LLM 護欄：有害性與 SHAP 可解釋性分析儀表板")
st.markdown("側邊欄選擇樣本，檢視模型對醫療 Prompt 的安全判斷與 SHAP 特徵貢獻分析。")
st.markdown("---")

if not data:
    st.warning("目前沒有載入任何資料，請確認 data.json 檔案是否存在與格式正確。")
    st.stop()

# 側邊欄：樣本選擇器
st.sidebar.header("🔍 控制面板")
sample_ids = [item["id"] for item in data]
selected_id = st.sidebar.selectbox("選擇分析樣本 ID (Sample ID)", sample_ids)

# 取得所選樣本的資料
selected_sample = next((item for item in data if item["id"] == selected_id), None)

if selected_sample:
    # 建立左右兩欄 (3:2 比例)
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("📝 樣本詳細資訊")

        # 顯示 Prompt 文字區塊
        st.markdown("**輸入提示詞 (Input Prompt):**")
        st.info(selected_sample.get("input_prompt", ""))

        # 基礎屬性指標
        m1, m2, m3 = st.columns(3)
        m1.metric("所屬原則 (Principle)", selected_sample.get("Principle", "").split(":")[0])
        m2.metric("真實標籤 (Ground Truth)", selected_sample.get("ground_truth", "N/A"))

        pred = selected_sample.get("prediction", "N/A")
        pred_color = "red" if pred in ["Malicious", "Harmful"] else "green"
        m3.metric("模型預測 (Prediction)", pred)

        st.markdown(
            f"**危害等級 (Harmfulness):** `{selected_sample.get('Harmfulness', 'N/A')}`"
        )
        st.markdown(
            f"**模型信心度 (Confidence):** `{selected_sample.get('confidence', 0)}%`"
        )

        st.markdown("---")
        st.subheader("📊 類別預測機率 (Probabilities)")

        # 類別機率長條圖 (Plotly)
        probs = selected_sample.get("probabilities", {})
        categories = list(probs.keys())
        prob_values = list(probs.values())

        fig_prob = go.Figure(
            go.Bar(
                x=prob_values,
                y=categories,
                orientation="h",
                marker=dict(
                    color=["#2ecc71" if c == "Benign" else "#e74c3c" for c in categories]
                ),
                text=[f"{v}%" for v in prob_values],
                textposition="auto",
            )
        )
        fig_prob.update_layout(
            height=220,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(title="Probability (%)", range=[0, 100]),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_prob, use_container_width=True)

    with col2:
        st.subheader("🧩 SHAP 特徵重要性分析")

        shap_list = selected_sample.get("shap_values", [])
        if shap_list:
            features = [item["feature"] for item in shap_list]
            shap_vals = [item["shap_value"] for item in shap_list]

            # 繪製 SHAP 貢獻條狀圖 (Matplotlib / Seaborn)
            fig_shap, ax = plt.subplots(figsize=(6, 5))
            colors = ["#3498db" if v >= 0 else "#e67e22" for v in shap_vals]

            y_pos = np.arange(len(features))
            ax.barh(y_pos, shap_vals, color=colors, align="center")
            ax.set_yticks(y_pos)
            ax.set_yticklabels(features)
            ax.invert_yaxis()  # 最高特徵放在最上面
            ax.set_xlabel("SHAP Value (Impact on Prediction)")
            ax.set_title("Feature Contribution (SHAP)")
            ax.grid(axis="x", linestyle="--", alpha=0.7)

            st.pyplot(fig_shap)
        else:
            st.warning("此樣本無可用之 SHAP 數據。")

    # 底部：總體數據統計資料表 preview
    st.markdown("---")
    with st.expander("📋 檢視全體 JSON 數據預覽"):
        st.json(data)
