"""
処理内容:
- E2E の入口になる最小ランナー

使い方:
- `python e2e/e2e_test_runner.py`
"""

from pathlib import Path
from datetime import datetime


def main() -> None:
    results_dir = Path(__file__).resolve().parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    output_path = results_dir / f"e2e_stub_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    output_path.write_text("E2E template runner executed.\n", encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()

