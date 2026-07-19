# 电商用户消费行为数据分析

基于 100 万+ 条电商用户行为数据，完成 **数据清洗 → SQL 多维分析 → RFM 用户画像 → 可视化报告** 的完整数据分析项目。

## 项目亮点

- 处理 **100 万+** 用户行为事件，覆盖浏览、加购、收藏、购买全链路
- 完成缺失值 / 重复值 / 异常值清洗，并输出清洗日志
- 使用 **SQL** 统计活跃度、复购率、品类偏好、转化漏斗
- 基于 **RFM** 识别 3 类核心用户：高价值用户、潜力用户、流失风险用户
- 输出可视化图表 + 分析报告 + 2 条可落地运营建议

## 技术栈

- Python：Pandas / NumPy / Matplotlib / Seaborn
- SQL：SQLite
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
