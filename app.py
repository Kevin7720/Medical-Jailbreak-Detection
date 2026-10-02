import json
import os
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# 1. 頁面配置與全域黑夜模式 CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="LLM Safety & Jailbreak Detection",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* 全域背景 */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }

    /* 鎖定中央內容區最大寬度 (900px) */
    .main .block-container {
        max-width: 900px !important;
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        margin: 0 auto;
    }

    /* Input Prompt 外部卡片樣式 */
    .prompt-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* 弱化頂部標題列 */
    .prompt-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        font-weight: 600;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 16px;
    }
    .prompt-title-sub {
        color: #6e7681;
        font-weight: 400;
    }

    /* 主體內容聚焦框 (Hero Box) */
    .prompt-content-card {
        background-color: #0d1117;
        border-left: 4px solid #58a6ff;
        border-top: 1px solid #21262d;
        border-right: 1px solid #21262d;
        border-bottom: 1px solid #21262d;
        border-radius: 0 8px 8px 0;
        padding: 20px 24px;
        margin-bottom: 20px;
    }

    /* 核心 Prompt 文字樣式 */
    .prompt-text {
        font-size: 24px;
        font-weight: 600;
        color: #ffffff;
        line-height: 1.5;
        letter-spacing: 0.2px;
        margin: 0;
    }

    .badge-container {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    /* 標籤文字 */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        border-radius: 18px;
        font-size: 15px;
        font-weight: 500;
        background-color: #21262d;
        border: 1px solid #30363d;
    }
    .badge-blue { color: #58a6ff; border-color: #1f6beb; }
    .badge-orange { color: #f0883e; border-color: #bd561d; }
    .badge-green { color: #3fb950; background-color: rgba(46, 160, 67, 0.15); border-color: #2ea043; }
    .badge-red { color: #f85149; background-color: rgba(248, 81, 73, 0.15); border-color: #f85149; }

    /* Prediction 結果字型與 layout */
    .status-malicious {
        color: #f85149;
        font-size: 34px;
        font-weight: 700;
        margin-top: 4px;
    }
    .status-benign {
        color: #3fb950;
        font-size: 34px;
        font-weight: 700;
        margin-top: 4px;
    }
    .ground-truth-row {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        font-size: 16px;
        color: #8b949e;
        margin-top: 6px;
        margin-bottom: 24px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 2. 資料載入 (相容 showcase_data.json 及 data.json)
# -----------------------------------------------------------------------------
@st.cache_data
def load_showcase_data():
    for file_path in ["data.json"]:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    return []


dataset = load_showcase_data()

if not dataset:
    st.error(
        "⚠️ 未偵測到 showcase_data.json 或 data.json，請確保 JSON 檔案放在專案根目錄。"
    )
    st.stop()

# -----------------------------------------------------------------------------
# 2.1 側邊欄：設置 Harmfulness 與 Principle 多選核取方塊 (Filter)
# -----------------------------------------------------------------------------
st.sidebar.markdown("## ⚙️ Filter Settings")

# 固定 Harmfulness 選項
harmfulness_options = ["Level 0", "Level 1", "Level 2", "Level 3"]
selected_harmfulness = st.sidebar.multiselect(
    "⚠️️ Harmfulness Level",
    options=harmfulness_options,
    default=[],  # 預設留空表示不篩選（顯示全部）
    placeholder="Select Levels (Empty = All)",
)

# 動態從資料庫中取得出現過的所有 Principle
all_principles = sorted(
    list({str(item.get("Principle", "")) for item in dataset if item.get("Principle")})
)
selected_principles = st.sidebar.multiselect(
    "📋 Principle",
    options=all_principles,
    default=[],  # 預設留空表示不篩選（顯示全部）
    placeholder="Select Principles (Empty = All)",
)

# 根據勾選條件過濾資料集
filtered_dataset = []
for item in dataset:
    item_harm = str(item.get("Harmfulness", ""))
    item_princ = str(item.get("Principle", ""))

    # 檢查 Harmfulness (若有選擇則必須包含)
    harm_match = (
        True
        if not selected_harmfulness
        else any(h.lower() in item_harm.lower() for h in selected_harmfulness)
    )

    # 檢查 Principle (若有選擇則必須包含)
    princ_match = (
        True if not selected_principles else (item_princ in selected_principles)
    )

    if harm_match and princ_match:
        filtered_dataset.append(item)

st.sidebar.markdown("---")

# -----------------------------------------------------------------------------
# 2.2 側邊欄：根據篩選後的清單切換 Sample
# -----------------------------------------------------------------------------
if not filtered_dataset:
    st.sidebar.warning("⚠️ 沒有符合篩選條件的 Sample")
    st.warning("⚠️ 沒有符合當前邊欄篩選條件的資料，請調整左側的 Harmfulness 或 Principle。")
    st.stop()

sample_ids = [item.get("id", f"Sample_{idx}") for idx, item in enumerate(filtered_dataset)]
selected_id = st.sidebar.selectbox("🔍 Select Evaluation Sample", sample_ids)

selected_item = next(
    (item for item in filtered_dataset if item.get("id") == selected_id), filtered_dataset[0]
)

# 解析欄位
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
# 3. 頂部 Evaluated Input Prompt 區塊 (高亮聚焦版)
# -----------------------------------------------------------------------------
st.markdown(
    f"""
<div class="prompt-box">
    <div class="prompt-header">
        <span>💬 EVALUATED INPUT PROMPT</span>
        <span class="prompt-title-sub">({prompt_id})</span>
    </div>
    <div class="prompt-content-card">
        <p class="prompt-text">{input_prompt}</p>
    </div>
    <div class="badge-container">
        <div class="badge badge-blue">📋 Principle: {principle}</div>
        <div class="badge badge-orange">⚠️ Harmfulness: {harmfulness_level}</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 4. Prediction Result & Ground Truth
# -----------------------------------------------------------------------------
st.markdown("### 🎯 Prediction Result")

pred_str = str(prediction_result).strip().lower()
gt_str = str(ground_truth).strip().lower()

is_malicious = pred_str in ["malicious", "jailbreak", "harmful"]
status_class = "status-malicious" if is_malicious else "status-benign"

st.markdown(
    f'<div class="{status_class}">{prediction_result}</div>',
    unsafe_allow_html=True,
)

gt_is_malicious = gt_str in ["malicious", "jailbreak", "harmful"]
is_match = (pred_str == gt_str) or (is_malicious == gt_is_malicious)

match_badge = (
    '<span class="badge badge-green">✓ Match</span>'
    if is_match
    else '<span class="badge badge-red">✗ Mismatch</span>'
)

st.markdown(
    f"""
<div class="ground-truth-row">
    <span>Ground Truth: <strong style="color:#f0f6fc;">{ground_truth}</strong></span>
    {match_badge}
    <span>| Confidence: <strong style="color:#f0f6fc;">{confidence:.2f}%</strong></span>
</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 5. Class Probabilities
# -----------------------------------------------------------------------------
st.markdown("### 📊 Class Probabilities")

if prob_data:
    classes = list(prob_data.keys())
    probs = [float(v) for v in prob_data.values()]
    
    colors = []
    for c in classes:
        c_low = c.lower()
        if c_low == "benign":
            colors.append("#3fb950")      # 綠色
        elif c_low == "harmful":
            colors.append("#f0883e")      # 橘黃色
        elif c_low == "jailbreak":
            colors.append("#f85149")      # 紅色
        else:
            colors.append("#58a6ff")      # 預設藍色

    max_prob = max(probs) if probs else 100
    x_max_prob = max(max_prob * 1.2, 100)

    fig_prob = go.Figure()
    fig_prob.add_trace(
        go.Bar(
            x=probs,
            y=classes,
            orientation="h",
            marker=dict(color=colors),
            text=[f"{p:.2f}%" for p in probs],
            textposition="outside",
            cliponaxis=False,
        )
    )

    fig_prob.update_layout(
        xaxis=dict(
            range=[0, x_max_prob],
            title="Probability (%)",
            showgrid=True,
            gridcolor="#21262d",
            zeroline=False,
        ),
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d1d9"),
        margin=dict(l=10, r=60, t=10, b=40),
        height=260,
    )
    st.plotly_chart(fig_prob, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. SHAP Feature Attribution (紫色系 + Top 2 特徵高亮變色)
# -----------------------------------------------------------------------------
st.markdown("### 🧬 SHAP Feature Attribution")

if shap_list:
    raw_features = [str(item.get("feature", "")) for item in shap_list]
    values = [float(item.get("shap_value", 0.0)) for item in shap_list]

    sorted_values = sorted(values, reverse=True)
    top2_threshold = sorted_values[1] if len(sorted_values) >= 2 else (sorted_values[0] if sorted_values else 0)

    shap_colors = [
        "#a371f7" if v >= top2_threshold else "#484f58"
        for v in values
    ]

    max_feat_len = max([len(f) for f in raw_features]) if raw_features else 10
    dynamic_left_margin = min(max(max_feat_len * 8, 120), 300)

    def truncate_label(label, max_len=36):
        return label if len(label) <= max_len else label[: max_len - 3] + "..."

    display_features = [truncate_label(f) for f in raw_features]

    min_val = min(values) if values else 0
    max_val = max(values) if values else 1.0
    
    x_min = 0 if min_val >= 0 else min_val * 1.2
    x_max = max_val * 1.25

    fig_shap = go.Figure()
    fig_shap.add_trace(
        go.Bar(
            x=values,
            y=display_features,
            orientation="h",
            marker=dict(color=shap_colors),
            text=[f"{v:+.3f}" if v < 0 else f"{v:.3f}" for v in values],
            textposition="outside",
            hovertext=raw_features,
            hoverinfo="text+x",
            cliponaxis=False,
        )
    )

    fig_shap.update_layout(
        xaxis=dict(
            range=[x_min, x_max],
            title="SHAP Value (Impact on Model)",
            showgrid=True,
            gridcolor="#21262d",
            zeroline=True,
            zerolinecolor="#8b949e",
            zerolinewidth=2,
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=12, color="#c9d1d9"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9d1d9"),
        margin=dict(l=dynamic_left_margin, r=70, t=10, b=40),
        height=320,
    )
    st.plotly_chart(fig_shap, use_container_width=True)
