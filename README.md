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

## 📊 Dataset & Evaluation Benchmark

All evaluation samples in this dashboard are drawn from the test set of **CARES-18K**:

- **Dataset**: **CARES-18K** (*Clinical Adversarial Robustness and Evaluation of Safety*)
- **Overview**: A benchmark dataset for evaluating the safety and robustness of LLMs in clinical and healthcare contexts. It consists of over **18,000 synthetic prompts** designed to probe both LLM vulnerabilities to adversarial jailbreak inputs and their tendency to over-refuse safe queries.
- **Coverage**:
  - **8 Medical Safety Principles**
  - **4 Graded Harmfulness Levels** (Level 0 – Level 3)
  - **4 Prompting Strategies** (*Direct, Indirect, Obfuscation, Role-play*)

---

## ✨ Key Features

- **🤖 Target LLM Selection**: Easily switch between multiple evaluated target models (e.g., Mistral-7B, Vicuna, Llama series).
- **⚙️ Multi-Level Filtering**: Filter dataset samples by **⚠ Harmfulness Levels** (Level 0 ~ 3) and **📋 Safety Principles** (e.g., Patient Privacy, Harmful Content).
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
