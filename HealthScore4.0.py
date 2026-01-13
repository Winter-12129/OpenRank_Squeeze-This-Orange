# -*- coding: utf-8 -*-
import streamlit as st
import os
import json
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt


# 页面配置
# ===============================
st.set_page_config(
    page_title="开源项目健康度分析系统",
    layout="wide"
)

DATA_DIR = "top_300_metrics"

# 工具函数
# ===============================
def find_json(root, keyword):
    if not root:
        return None
    for f in os.listdir(root):
        if keyword in f.lower() and f.endswith(".json"):
            return os.path.join(root, f)
    return None


def parse_series(path):
    if not path or not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    values = []

    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, dict):
                values.append(sum(x for x in v.values() if isinstance(x, (int, float))))
            elif isinstance(v, (int, float)):
                values.append(v)

    return values if values else None


def safe_mean(x, window):
    if not x:
        return 0
    return np.mean(x[-window:])


# ===============================
# 主程序
# ===============================
def main():
    st.title("开源项目健康度分析系统")

    # ========== 项目扫描 ==========
    projects = []
    for root, _, files in os.walk(DATA_DIR):
        if any(f.endswith(".json") for f in files):
            projects.append(root)

    projects = sorted(set(projects))

    if not projects:
        st.error("未发现任何项目数据")
        st.stop()

    # ========== Sidebar ==========
    analysis_mode = st.sidebar.radio(
        "分析模式",
        ["单项目深度分析", "项目横向对比"]
    )

    window = st.sidebar.slider("分析窗口（月）", 3, 24, 12)

    st.sidebar.subheader("健康度权重")
    w_a = st.sidebar.slider("活跃度", 0.0, 1.0, 0.3)
    w_i = st.sidebar.slider("影响力", 0.0, 1.0, 0.3)
    w_c = st.sidebar.slider("协作度", 0.0, 1.0, 0.25)
    w_m = st.sidebar.slider("维护压力", 0.0, 1.0, 0.15)

    # 单项目分析
    # ===============================
    if analysis_mode == "单项目深度分析":
        selected = st.sidebar.selectbox(
            "选择项目",
            projects,
            format_func=lambda x: x.replace(DATA_DIR + os.sep, "")
        )

        activity = parse_series(find_json(selected, "activity") or find_json(selected, "commit"))
        impact = parse_series(find_json(selected, "openrank") or find_json(selected, "star"))
        collaboration = parse_series(find_json(selected, "contributor") or find_json(selected, "pull"))
        issues = parse_series(find_json(selected, "issue"))

        if not activity or not impact:
            st.error("该项目核心指标数据不完整，无法分析")
            st.stop()

        L = min(len(activity), len(impact))
        activity = activity[-L:]
        impact = impact[-L:]
        collaboration = collaboration[-L:] if collaboration else [0]*L
        issues = issues[-L:] if issues else [0]*L

        A = safe_mean(activity, window)
        I = safe_mean(impact, window)
        C = safe_mean(collaboration, window)
        M = safe_mean(issues, window)

        A_n = math.log1p(A)
        I_n = math.log1p(I)
        C_n = math.log1p(C)
        M_n = math.log1p(M)

        health = (
            w_a * A_n +
            w_i * I_n +
            w_c * C_n +
            w_m * (1 - M_n / (M_n + 1))
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("健康值", f"{health:.2f}")
        c2.metric("活跃度", f"{A:.1f}")
        c3.metric("影响力", f"{I:.1f}")
        c4.metric("协作度", f"{C:.1f}")

        st.subheader("多指标趋势")
        df_trend = pd.DataFrame({
            "Activity": activity[-window:],
            "Impact": impact[-window:],
            "Collaboration": collaboration[-window:]
        })
        st.line_chart(df_trend)

        st.subheader("健康结构雷达图")
        labels = ["Activity", "Impact", "Collaboration", "Maintenance"]
        values = [A_n, I_n, C_n, 1 - M_n/(M_n+1)]
        values += values[:1]
        angles = np.linspace(0, 2*np.pi, len(labels)+1)

        fig = plt.figure()
        ax = plt.subplot(111, polar=True)
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.3)
        ax.set_thetagrids(angles[:-1]*180/np.pi, labels)
        st.pyplot(fig)

        st.subheader("活跃度 vs 影响力")
        fig2 = plt.figure()
        plt.scatter(activity[-window:], impact[-window:], alpha=0.6)
        plt.xlabel("Activity")
        plt.ylabel("Impact")
        plt.grid(True)
        st.pyplot(fig2)

        st.subheader("Issue 维护压力趋势")
        fig3 = plt.figure()
        plt.plot(issues[-window:])
        plt.xlabel("Time")
        plt.ylabel("Issues")
        plt.grid(True)
        st.pyplot(fig3)

    # 横向对比分析
    # ===============================
    else:
        st.header("项目健康度横向对比分析")

        records = []

        for p in projects:
            activity = parse_series(find_json(p, "activity") or find_json(p, "commit"))
            impact = parse_series(find_json(p, "openrank") or find_json(p, "star"))
            collaboration = parse_series(find_json(p, "contributor") or find_json(p, "pull"))
            issues = parse_series(find_json(p, "issue"))

            if not activity or not impact:
                continue

            A = safe_mean(activity, window)
            I = safe_mean(impact, window)
            C = safe_mean(collaboration, window)
            M = safe_mean(issues, window)

            health = (
                w_a * math.log1p(A) +
                w_i * math.log1p(I) +
                w_c * math.log1p(C) +
                w_m * (1 - math.log1p(M) / (math.log1p(M) + 1))
            )

            records.append({
                "Project": p.replace(DATA_DIR + os.sep, ""),
                "Health": health,
                "Activity": A,
                "Impact": I
            })

        df = pd.DataFrame(records)

        if df.empty:
            st.warning("没有足够数据用于横向对比")
            st.stop()

        top_n = st.slider("显示前 N 个项目", 5, 50, 20)

        st.subheader(" Top 健康项目")
        st.bar_chart(
            df.sort_values("Health", ascending=False)
              .head(top_n)
              .set_index("Project")["Health"]
        )

        st.subheader(" 健康值分布")
        fig = plt.figure()
        plt.hist(df["Health"], bins=20)
        plt.xlabel("Health Score")
        plt.ylabel("Projects")
        plt.grid(True)
        st.pyplot(fig)

        st.subheader(" 活跃度 vs 影响力")
        fig2 = plt.figure()
        plt.scatter(df["Activity"], df["Impact"], alpha=0.6)
        plt.xlabel("Activity")
        plt.ylabel("Impact")
        plt.grid(True)
        st.pyplot(fig2)


if __name__ == "__main__":
    main()
