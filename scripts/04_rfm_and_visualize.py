"""
RFM 用户分群 + 可视化 + 运营建议报告
三类核心用户：高价值用户 / 潜力用户 / 流失风险用户
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
import seaborn as sns

# 中文字体：优先使用 Windows 已安装字体，避免中文缺字
def _setup_chinese_font() -> None:
    candidates = [
        r"C:\Windows\Fonts\msyh.ttc",      # 微软雅黑
        r"C:\Windows\Fonts\simhei.ttf",    # 黑体
        r"C:\Windows\Fonts\simsun.ttc",    # 宋体
    ]
    for path in candidates:
        if Path(path).exists():
            font_manager.fontManager.addfont(path)
            font_name = font_manager.FontProperties(fname=path).get_name()
            plt.rcParams["font.family"] = font_name
            plt.rcParams["font.sans-serif"] = [font_name]
            break
    plt.rcParams["axes.unicode_minus"] = False


_setup_chinese_font()
sns.set_theme(style="whitegrid")
# seaborn 可能覆盖字体，再设一次
_setup_chinese_font()

ROOT = Path(__file__).resolve().parents[1]
CLEAN_CSV = ROOT / "data" / "processed" / "user_behavior_clean.csv"
FIG_DIR = ROOT / "output" / "figures"
REPORT_DIR = ROOT / "output" / "reports"
FIG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_rfm(df: pd.DataFrame) -> pd.DataFrame:
    buy = df[df["behavior"] == "buy"].copy()
    if buy.empty:
        raise ValueError("没有购买行为数据，无法构建 RFM")

    snapshot = buy["timestamp"].max() + pd.Timedelta(days=1)
    rfm = (
        buy.groupby("user_id")
        .agg(
            last_buy=("timestamp", "max"),
            frequency=("timestamp", "count"),
            monetary=("price", "sum"),
        )
        .reset_index()
    )
    rfm["recency"] = (snapshot - rfm["last_buy"]).dt.days

    # 分位数打分：R 越小越好，F/M 越大越好
    rfm["R_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

    def segment(row: pd.Series) -> str:
        # 三类核心用户（简历可直接写）
        if row["R_score"] >= 4 and row["F_score"] >= 4 and row["M_score"] >= 4:
            return "高价值用户"
        if row["R_score"] >= 3 and (row["F_score"] >= 3 or row["M_score"] >= 3):
            return "潜力用户"
        return "流失风险用户"

    rfm["segment"] = rfm.apply(segment, axis=1)
    return rfm


def plot_figures(df: pd.DataFrame, rfm: pd.DataFrame) -> dict:
    paths = {}

    # 1) 行为分布
    fig, ax = plt.subplots(figsize=(8, 5))
    order = ["pv", "cart", "fav", "buy"]
    sns.countplot(data=df, x="behavior", order=order, ax=ax, hue="behavior", palette="Blues_d", legend=False)
    ax.set_title("用户行为分布")
    ax.set_xlabel("行为类型")
    ax.set_ylabel("事件数")
    p = FIG_DIR / "01_behavior_distribution.png"
    fig.tight_layout()
    fig.savefig(p, dpi=150)
    plt.close(fig)
    paths["behavior"] = p

    # 2) DAU 趋势
    dau = df.groupby(df["timestamp"].dt.date)["user_id"].nunique()
    fig, ax = plt.subplots(figsize=(10, 5))
    dau.plot(ax=ax, marker="o", color="#2c7fb8")
    ax.set_title("日活跃用户（DAU）趋势")
    ax.set_xlabel("日期")
    ax.set_ylabel("DAU")
    p = FIG_DIR / "02_dau_trend.png"
    fig.tight_layout()
    fig.savefig(p, dpi=150)
    plt.close(fig)
    paths["dau"] = p

    # 3) 品类 GMV
    buy = df[df["behavior"] == "buy"]
    cat = buy.groupby("category", observed=True)["price"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    cat.plot(kind="bar", ax=ax, color="#41b6c4")
    ax.set_title("各品类 GMV")
    ax.set_xlabel("品类")
    ax.set_ylabel("GMV")
    plt.xticks(rotation=30, ha="right")
    p = FIG_DIR / "03_category_gmv.png"
    fig.tight_layout()
    fig.savefig(p, dpi=150)
    plt.close(fig)
    paths["category"] = p

    # 4) 小时活跃
    hour = df.groupby("hour")["user_id"].count()
    fig, ax = plt.subplots(figsize=(10, 5))
    hour.plot(kind="line", marker="o", ax=ax, color="#253494")
    ax.set_title("24 小时活跃分布")
    ax.set_xlabel("小时")
    ax.set_ylabel("事件数")
    ax.set_xticks(range(0, 24))
    p = FIG_DIR / "04_hour_activity.png"
    fig.tight_layout()
    fig.savefig(p, dpi=150)
    plt.close(fig)
    paths["hour"] = p

    # 5) 用户分群占比
    seg = rfm["segment"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 7))
    colors = ["#2c7fb8", "#7fcdbb", "#f03b20"]
    ax.pie(seg.values, labels=seg.index, autopct="%1.1f%%", startangle=90, colors=colors[: len(seg)])
    ax.set_title("三类核心用户群体占比")
    p = FIG_DIR / "05_user_segments.png"
    fig.tight_layout()
    fig.savefig(p, dpi=150)
    plt.close(fig)
    paths["segment"] = p

    # 6) RFM 散点（F vs M，颜色=R）
    sample = rfm.sample(n=min(3000, len(rfm)), random_state=42)
    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(sample["frequency"], sample["monetary"], c=sample["recency"], cmap="viridis_r", alpha=0.6, s=18)
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label("Recency(天，越小越好)")
    ax.set_title("RFM 散点图（Frequency vs Monetary）")
    ax.set_xlabel("Frequency（购买次数）")
    ax.set_ylabel("Monetary（消费金额）")
    p = FIG_DIR / "06_rfm_scatter.png"
    fig.tight_layout()
    fig.savefig(p, dpi=150)
    plt.close(fig)
    paths["rfm"] = p

    return paths


def write_report(df: pd.DataFrame, rfm: pd.DataFrame) -> Path:
    total_events = len(df)
    total_users = df["user_id"].nunique()
    buy = df[df["behavior"] == "buy"]
    buy_users = buy["user_id"].nunique()
    gmv = buy["price"].sum()
    avg_order = buy["price"].mean() if len(buy) else 0

    # 复购
    buy_cnt = buy.groupby("user_id").size()
    repurchase_rate = (buy_cnt >= 2).mean() if len(buy_cnt) else 0

    # 转化（用户级）
    user_flags = df.groupby("user_id")["behavior"].agg(lambda s: set(s))
    pv_users = sum("pv" in s for s in user_flags)
    cart_users = sum("cart" in s for s in user_flags)
    pv_to_buy = buy_users / pv_users if pv_users else 0
    cart_to_buy = buy_users / cart_users if cart_users else 0

    seg_stats = (
        rfm.groupby("segment")
        .agg(
            users=("user_id", "count"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
            total_gmv=("monetary", "sum"),
        )
        .round(2)
    )
    seg_stats["user_ratio"] = (seg_stats["users"] / seg_stats["users"].sum()).round(4)

    # 两条运营建议（对应简历）
    top_cat = buy.groupby("category", observed=True)["price"].sum().sort_values(ascending=False).index[0]
    peak_hour = int(df.groupby("hour")["user_id"].count().idxmax())

    lines = [
        "# 电商用户消费行为数据分析报告",
        "",
        "## 1. 项目概述",
        "基于电商用户行为数据，完成数据清洗、探索性分析、SQL 多维统计与 RFM 用户画像构建，",
        "识别核心用户群体并输出可落地的运营建议。",
        "",
        "## 2. 数据概况",
        f"- 分析事件数：{total_events:,}",
        f"- 用户数：{total_users:,}",
        f"- 购买用户数：{buy_users:,}",
        f"- GMV：{gmv:,.2f}",
        f"- 客单价：{avg_order:,.2f}",
        f"- 复购率：{repurchase_rate:.2%}",
        f"- 浏览→购买转化率：{pv_to_buy:.2%}",
        f"- 加购→购买转化率：{cart_to_buy:.2%}",
        "",
        "## 3. 三类核心用户群体",
        seg_stats.to_markdown(),
        "",
        "### 群体解读",
        "- **高价值用户**：近期活跃、购买频次高、贡献金额大，是利润核心来源。",
        "- **潜力用户**：有一定活跃与消费基础，可通过精准运营提升复购与客单。",
        "- **流失风险用户**：久未购买或消费偏低，需要召回与刺激。",
        "",
        "## 4. 关键洞察",
        f"- GMV 最高品类：{top_cat}",
        f"- 用户活跃高峰时段：{peak_hour}:00 左右",
        f"- 高价值用户人数占比约 {seg_stats.loc['高价值用户', 'user_ratio']:.1%}，但贡献了显著更高的人均消费。",
        "",
        "## 5. 两条针对性运营建议",
        "1. **高价值用户会员化运营**：对高价值用户发放专属优惠券/积分加速、优先发货与新品试用，",
        "   目标是提升其月复购次数与客单价，稳住核心 GMV。",
        f"2. **峰时场景化转化 + 潜力用户促活**：在每日 {peak_hour} 点前后加大「{top_cat}」等优势品类的限时活动与加购提醒，",
        "   同时对潜力用户做「加购未购」召回，提高浏览/加购到购买的转化率。",
        "",
        "## 6. 产出清单",
        "- 清洗日志：`output/reports/data_cleaning_log.txt`",
        "- SQL 分析结果：`output/reports/sql_analysis_summary.md`",
        "- 用户分群明细：`output/reports/rfm_user_segments.csv`",
        "- 可视化图表：`output/figures/`",
        "",
        "## 7. 技术栈",
        "Python（Pandas / NumPy / Matplotlib / Seaborn） + SQL（SQLite）",
        "",
    ]

    report_path = REPORT_DIR / "analysis_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> None:
    print("读取清洗数据...")
    df = pd.read_csv(CLEAN_CSV, parse_dates=["timestamp"])

    print("构建 RFM 并分群...")
    rfm = build_rfm(df)
    rfm_path = REPORT_DIR / "rfm_user_segments.csv"
    rfm.to_csv(rfm_path, index=False, encoding="utf-8-sig")

    print("生成可视化...")
    plot_figures(df, rfm)

    print("撰写分析报告...")
    report_path = write_report(df, rfm)

    print("分群人数：")
    print(rfm["segment"].value_counts())
    print(f"RFM 明细: {rfm_path}")
    print(f"分析报告: {report_path}")
    print(f"图表目录: {FIG_DIR}")


if __name__ == "__main__":
    main()
