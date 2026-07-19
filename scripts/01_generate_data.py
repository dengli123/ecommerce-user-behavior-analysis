"""
生成模拟电商用户行为数据（约 100 万+ 条）
字段：user_id, item_id, category, behavior, timestamp, price, province
behavior: pv(浏览) / cart(加购) / fav(收藏) / buy(购买)
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
N_ROWS = 1_050_000  # 100万+，清洗后仍可保持百万级
N_USERS = 80_000
N_ITEMS = 12_000

CATEGORIES = [
    "数码家电",
    "服饰鞋包",
    "美妆个护",
    "食品生鲜",
    "家居日用",
    "运动户外",
    "母婴用品",
    "图书文娱",
]
BEHAVIORS = ["pv", "cart", "fav", "buy"]
# 真实电商漏斗：浏览远多于购买
BEHAVIOR_PROBS = [0.78, 0.10, 0.07, 0.05]
PROVINCES = [
    "广东", "浙江", "江苏", "山东", "河南", "四川", "湖北", "湖南",
    "福建", "安徽", "北京", "上海", "河北", "陕西", "辽宁", "江西",
]


def main() -> None:
    rng = np.random.default_rng(SEED)
    print(f"开始生成 {N_ROWS:,} 条模拟用户行为数据...")

    # 用户活跃度长尾分布：少数高活用户贡献大量行为
    user_weights = rng.pareto(a=1.5, size=N_USERS) + 0.1
    user_weights = user_weights / user_weights.sum()
    user_ids = rng.choice(np.arange(1, N_USERS + 1), size=N_ROWS, p=user_weights)

    item_ids = rng.integers(1, N_ITEMS + 1, size=N_ROWS)
    categories = rng.choice(CATEGORIES, size=N_ROWS)
    behaviors = rng.choice(BEHAVIORS, size=N_ROWS, p=BEHAVIOR_PROBS)
    provinces = rng.choice(PROVINCES, size=N_ROWS)

    # 30 天时间窗口
    start = np.datetime64("2025-03-01T00:00:00")
    offsets = rng.integers(0, 30 * 24 * 3600, size=N_ROWS)
    timestamps = start + offsets.astype("timedelta64[s]")

    # 价格：按品类给不同区间，购买行为价格略高一点更合理
    base_price = rng.uniform(9.9, 899.0, size=N_ROWS)
    price_factor = np.where(behaviors == "buy", rng.uniform(1.0, 1.3, size=N_ROWS), 1.0)
    prices = np.round(base_price * price_factor, 2)

    df = pd.DataFrame(
        {
            "user_id": user_ids,
            "item_id": item_ids,
            "category": categories,
            "behavior": behaviors,
            "timestamp": timestamps,
            "price": prices,
            "province": provinces,
        }
    )

    # 故意注入脏数据，方便清洗环节展示
    dirty_n = 8000
    dirty_idx = rng.choice(df.index, size=dirty_n, replace=False)
    # 缺失值
    df.loc[dirty_idx[:2000], "category"] = np.nan
    df.loc[dirty_idx[2000:3500], "price"] = np.nan
    df.loc[dirty_idx[3500:4500], "province"] = ""
    # 异常价格
    df.loc[dirty_idx[4500:5500], "price"] = -1
    df.loc[dirty_idx[5500:6000], "price"] = 999999
    # 非法行为类型
    df.loc[dirty_idx[6000:6500], "behavior"] = "unknown"
    # 重复行
    dup = df.sample(n=3000, random_state=SEED)
    df = pd.concat([df, dup], ignore_index=True)

    out_path = RAW_DIR / "user_behavior_raw.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"原始数据已保存: {out_path}")
    print(f"总行数: {len(df):,}")
    print(f"用户数: {df['user_id'].nunique():,}")
    print(f"商品数: {df['item_id'].nunique():,}")
    print("行为分布:")
    print(df["behavior"].value_counts(dropna=False))


if __name__ == "__main__":
    main()
