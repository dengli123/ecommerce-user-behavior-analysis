"""
一键运行完整分析流程：
1) 生成模拟数据
2) 数据清洗
3) SQL 多维分析
4) RFM 分群 + 可视化 + 报告
"""
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    ROOT / "scripts" / "01_generate_data.py",
    ROOT / "scripts" / "02_clean_data.py",
    ROOT / "scripts" / "03_sql_analysis.py",
    ROOT / "scripts" / "04_rfm_and_visualize.py",
]


def main() -> None:
    for script in SCRIPTS:
        print("\n" + "=" * 60)
        print(f"Running: {script.name}")
        print("=" * 60)
        runpy.run_path(str(script), run_name="__main__")
    print("\n全部完成！请查看 output/ 目录下的图表与报告。")


if __name__ == "__main__":
    main()
