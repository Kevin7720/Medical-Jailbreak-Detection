# 🛡️ LLM Safety & Jailbreak Detection Interactive Visualizer

An interactive Streamlit web interface for evaluating **LLM Safety and Jailbreak Detection**. This tool provides transparent model probability breakdowns and SHAP feature attributions across various target Large Language Models (LLMs).

---

## 🎬 Demo Preview

![App Demo](assets/demo.gif)

---

## 🚀 Quick Start

**Please click this button to start:**
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://testclassifier-6jws7wrtheqybytqfasnzp.streamlit.app/)

---

## ✨ Key Features

- **🤖 Target LLM Selection**: Easily switch between multiple evaluated target models (e.g., Mistral-7B, Vicuna, Llama series).
- **⚙️ Multi-Level Filtering**: Filter dataset samples by **⚠ Harmfulness Levels** (Level 0 ~ 3) and **📋Safety Principles** (e.g., Patient Privacy, Harmful Content).
- **📊 Class Probabilities Breakdown**: Color-coded visualization showing the model's confidence across `Benign`, `Harmful`, and `Jailbreak` categories.
- **🧩 SHAP Feature Attribution Analysis**: Distinctive visualization highlighting the **Top 2 key features** (`#a371f7`) that drove the classifier's detection result.

---

## 🎯 Supported Target LLMs

The visualizer currently integrates analysis datasets for:
- `Mistral-7B`
- `Vicuna-7b`
- `Vicuna-13b`
- `Llama2-7B`
- `Llama3-8B`

