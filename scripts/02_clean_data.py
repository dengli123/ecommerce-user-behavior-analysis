"""
数据清洗：缺失值、重复值、异常值、非法枚举
输出清洗后数据 + 清洗日志
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "user_behavior_raw.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "output" / "reports"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

VALID_BEHAVIORS = {"pv", "cart", "fav", "buy"}
PRICE_MIN, PRICE_MAX = 1.0, 5000.0


def main() -> None:
    print("读取原始数据...")
    df = pd.read_csv(RAW_PATH, parse_dates=["timestamp"])
    before = len(df)
    logs = [f"原始行数: {before:,}"]

    # 1) 去重
    df = df.drop_duplicates()
    logs.append(f"去重后: {len(df):,}（删除 {before - len(df):,}）")

    # 2) 行为类型合法化
    invalid_behavior = ~df["behavior"].isin(VALID_BEHAVIORS)
    logs.append(f"非法 behavior 行数: {invalid_behavior.sum():,}")
    df = df.loc[~invalid_behavior].copy()

    # 3) 省份空字符串转缺失
    df["province"] = df["province"].replace("", pd.NA)

    # 4) 缺失值处理
    miss_before = df.isna().sum()
    logs.append("缺失值统计(处理前):")
    for col, cnt in miss_before.items():
        if cnt > 0:
            logs.append(f"  - {col}: {cnt:,}")

    # category / province 用众数填充；price 用中位数填充
    if df["category"].isna().any():
        df["category"] = df["category"].fillna(df["category"].mode(dropna=True)[0])
    if df["province"].isna().any():
        df["province"] = df["province"].fillna(df["province"].mode(dropna=True)[0])
    if df["price"].isna().any():
        df["price"] = df["price"].fillna(df["price"].median())

    # 5) 价格异常值
    price_bad = (df["price"] < PRICE_MIN) | (df["price"] > PRICE_MAX)
    logs.append(f"价格异常行数: {price_bad.sum():,}")
    df = df.loc[~price_bad].copy()

    # 6) 时间字段规范化 + 衍生字段
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date.astype(str)
    df["hour"] = df["timestamp"].dt.hour
    df["weekday"] = df["timestamp"].dt.day_name()

    # 7) 类型优化
    df["user_id"] = df["user_id"].astype("int32")
    df["item_id"] = df["item_id"].astype("int32")
    df["behavior"] = df["behavior"].astype("category")
    df["category"] = df["category"].astype("category")
    df["province"] = df["province"].astype("category")

    after = len(df)
    logs.append(f"清洗后行数: {after:,}")
    logs.append(f"总删除比例: {(before - after) / before:.2%}")
    logs.append(f"用户数: {df['user_id'].nunique():,}")
    logs.append(f"商品数: {df['item_id'].nunique():,}")

    out_csv = PROCESSED_DIR / "user_behavior_clean.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    logs.append(f"清洗数据已保存: {out_csv}")

    # 另存一份便于 SQLite 导入的精简字段
    slim = df[["user_id", "item_id", "category", "behavior", "timestamp", "price", "province", "date", "hour"]]
    slim_path = PROCESSED_DIR / "user_behavior_clean_slim.csv"
    slim.to_csv(slim_path, index=False, encoding="utf-8-sig")

    log_path = REPORT_DIR / "data_cleaning_log.txt"
    log_path.write_text("\n".join(logs), encoding="utf-8")
    print("\n".join(logs))
    print(f"清洗日志: {log_path}")


if __name__ == "__main__":
    main()
