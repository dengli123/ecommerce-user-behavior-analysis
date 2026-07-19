# 电商用户消费行为数据分析

基于 100 万+ 条电商用户行为数据，完成 **数据清洗 → SQL 多维分析 → RFM 用户画像 → 可视化报告** 的完整数据分析项目。

> 适合简历项目展示：数据分析 / 数据运营 / 业务分析 实习岗

## 项目亮点

- 处理 **100 万+** 用户行为事件，覆盖浏览、加购、收藏、购买全链路
- 完成缺失值 / 重复值 / 异常值清洗，并输出清洗日志
- 使用 **SQL** 统计活跃度、复购率、品类偏好、转化漏斗
- 基于 **RFM** 识别 3 类核心用户：高价值用户、潜力用户、流失风险用户
- 输出可视化图表 + 分析报告 + 2 条可落地运营建议

## 技术栈

- Python：Pandas / NumPy / Matplotlib / Seaborn
- SQL：SQLite（语法兼容 MySQL 常见写法）
- 工具：VS Code / Git / GitHub

## 目录结构

```text
ecommerce-user-behavior-analysis/
├── data/
│   ├── raw/                 # 原始数据（本地生成，默认不上传）
│   └── processed/           # 清洗后数据 / SQLite
├── scripts/
│   ├── 01_generate_data.py  # 生成模拟数据
│   ├── 02_clean_data.py     # 数据清洗
│   ├── 03_sql_analysis.py   # SQL 多维分析
│   └── 04_rfm_and_visualize.py  # RFM + 可视化 + 报告
├── sql/
│   └── analysis_queries.sql # SQL 查询脚本
├── output/
│   ├── figures/             # 图表
│   └── reports/             # 报告与中间结果
├── run_all.py               # 一键运行
├── requirements.txt
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 一键运行全流程

```bash
python run_all.py
```

或分步执行：

```bash
python scripts/01_generate_data.py
python scripts/02_clean_data.py
python scripts/03_sql_analysis.py
python scripts/04_rfm_and_visualize.py
```

### 3. 查看结果

- 分析报告：`output/reports/analysis_report.md`
- SQL 摘要：`output/reports/sql_analysis_summary.md`
- 用户分群：`output/reports/rfm_user_segments.csv`
- 图表：`output/figures/`

## 分析内容说明

| 模块 | 内容 |
|------|------|
| 数据清洗 | 去重、非法行为过滤、缺失填充、价格异常剔除 |
| 活跃分析 | DAU 趋势、24 小时活跃分布 |
| 转化分析 | 浏览→购买、加购→购买转化率 |
| 消费偏好 | 品类 GMV、省份 GMV Top10 |
| 用户画像 | RFM 打分与 3 类用户分群 |
| 运营建议 | 高价值用户会员化、峰时转化与潜力用户促活 |

## 简历可写版本（可直接粘贴）

**电商用户消费行为数据分析**（2025.03–2025.04）  
技术栈：Python（Pandas/Matplotlib/Seaborn）+ SQL  

- 对 100 万+ 条用户行为数据进行清洗，处理缺失值、重复值与异常值  
- 使用 SQL 统计用户活跃度、复购率、品类偏好与转化漏斗  
- 基于 RFM 构建用户画像，识别高价值 / 潜力 / 流失风险 3 类核心用户  
- 输出完整分析报告与可视化图表，提出 2 条针对性运营建议  

项目地址：`https://github.com/你的用户名/ecommerce-user-behavior-analysis`

## 说明

本项目使用可复现的模拟数据（固定随机种子），完整演示数据分析全流程。  
你也可以将 `scripts/01_generate_data.py` 替换为真实公开数据集后复用后续脚本。
