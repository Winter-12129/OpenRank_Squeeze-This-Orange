# OpenRank_Squeeze-This-Orange
项目简介
本项目是一个基于OpenDigger的开源项目健康度分析系统，通过多维指标对开源项目进行量化评估与可视化分析。该项目完整覆盖了数据读取、数据处理、建模分析、可视化展示以及简单应用系统构建等内容。

系统整体技术路线
OpenDigger JSON 数据
        ↓
数据自动扫描与解析
        ↓
时间序列构建与数值处理
        ↓
多维健康度模型构建
        ↓
单项目纵向分析 & 多项目横向对比
        ↓
可视化展示


实验结果分析与交互式前端的实现
单项目纵向分析：健康值 KPI 显示、多指标时间趋势图、健康结构雷达图、Issue 维护压力分析
多项目横向对比分析：计算所有项目健康值、排序并展示 Top-N 项目、分析健康度整体分布


健康度模型设计
项目健康度四个维度构成：活跃度、影响力、协作度、维护压力
健康度计算公式：
Health =w₁ · Activity+ w₂ · Impact+ w₃ · Collaboration+ w₄ · (1 − IssuePressure)



项目结构
├── HealthScore4.0.py        # 主程序
├── top_300_metrics/            # OpenDigger 数据目录
├── 项目报告.pdf                     # 报告
├── HealthScore.ppt              # 汇报 PPT
├── 汇报视频.MP4                # 讲解视频
└── README.md                   # 项目说明文件



运行方式
pip install streamlit numpy pandas matplotlib
streamlit run HealthScore_Final.py
http://localhost:8501


作者说明
本项目为课程设计作业，仅用于教学与学习目的

所使用数据来源于 OpenDigger 开源项目数据集