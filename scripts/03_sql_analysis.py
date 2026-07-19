"""
使用 SQLite 执行多维 SQL 分析（无需安装 MySQL，简历可写 SQL + 复杂查询）
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN_CSV = ROOT / "data" / "processed" / "user_behavior_clean_slim.csv"
DB_PATH = ROOT / "data" / "processed" / "ecommerce.db"
REPORT_DIR = ROOT / "output" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


QUERIES = {
    "01_behavior_funnel": """
        SELECT behavior,
               COUNT(*) AS event_cnt,
               COUNT(DISTINCT user_id) AS user_cnt
        FROM user_behavior
        GROUP BY behavior
        ORDER BY event_cnt DESC;
    """,
    "02_dau": """
        SELECT date,
               COUNT(DISTINCT user_id) AS dau
        FROM user_behavior
        GROUP BY date
        ORDER BY date;
    """,
    "03_repurchase_rate": """
        WITH buy_users AS (
            SELECT user_id, COUNT(*) AS buy_cnt
            FROM user_behavior
            WHERE behavior = 'buy'
            GROUP BY user_id
        )
        SELECT COUNT(*) AS buy_user_cnt,
               SUM(CASE WHEN buy_cnt >= 2 THEN 1 ELSE 0 END) AS repurchase_user_cnt,
               ROUND(1.0 * SUM(CASE WHEN buy_cnt >= 2 THEN 1 ELSE 0 END) / COUNT(*), 4) AS repurchase_rate
        FROM buy_users;
    """,
    "04_category_preference": """
        SELECT category,
               COUNT(*) AS buy_orders,
               COUNT(DISTINCT user_id) AS buy_users,
               ROUND(SUM(price), 2) AS gmv,
               ROUND(AVG(price), 2) AS avg_price
        FROM user_behavior
        WHERE behavior = 'buy'
        GROUP BY category
        ORDER BY gmv DESC;
    """,
    "05_province_gmv_top10": """
        SELECT province,
               ROUND(SUM(price), 2) AS gmv,
               COUNT(DISTINCT user_id) AS buyers
        FROM user_behavior
        WHERE behavior = 'buy'
        GROUP BY province
        ORDER BY gmv DESC
        LIMIT 10;
    """,
    "06_hour_activity": """
        SELECT hour,
               COUNT(*) AS event_cnt,
               COUNT(DISTINCT user_id) AS user_cnt
        FROM user_behavior
        GROUP BY hour
        ORDER BY hour;
    """,
    "07_conversion": """
        WITH users AS (
            SELECT user_id,
                   MAX(CASE WHEN behavior = 'pv' THEN 1 ELSE 0 END) AS has_pv,
                   MAX(CASE WHEN behavior = 'cart' THEN 1 ELSE 0 END) AS has_cart,
                   MAX(CASE WHEN behavior = 'buy' THEN 1 ELSE 0 END) AS has_buy
            FROM user_behavior
            GROUP BY user_id
        )
        SELECT SUM(has_pv) AS pv_users,
               SUM(has_cart) AS cart_users,
               SUM(has_buy) AS buy_users,
               ROUND(1.0 * SUM(has_buy) / NULLIF(SUM(has_pv), 0), 4) AS pv_to_buy_rate,
               ROUND(1.0 * SUM(has_buy) / NULLIF(SUM(has_cart), 0), 4) AS cart_to_buy_rate
        FROM users;
    """,
}


def main() -> None:
    print("导入清洗数据到 SQLite...")
    df = pd.read_csv(CLEAN_CSV)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("user_behavior", conn, index=False, if_exists="replace")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_user ON user_behavior(user_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_behavior ON user_behavior(behavior);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON user_behavior(date);")
    conn.commit()

    summary_lines = ["# SQL 多维分析结果摘要", ""]
    for name, sql in QUERIES.items():
        print(f"执行查询: {name}")
        result = pd.read_sql_query(sql, conn)
        out_path = REPORT_DIR / f"{name}.csv"
        result.to_csv(out_path, index=False, encoding="utf-8-sig")
        summary_lines.append(f"## {name}")
        summary_lines.append(result.to_string(index=False))
        summary_lines.append("")

    conn.close()
    summary_path = REPORT_DIR / "sql_analysis_summary.md"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    print(f"SQL 分析完成，结果目录: {REPORT_DIR}")
    print(f"摘要: {summary_path}")


if __name__ == "__main__":
    main()
