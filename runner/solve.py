#!/usr/bin/env python3
"""川渡りパズル求解 CLI。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from river_crossing_ip.engine import Engine
from river_crossing_ip.load_data import SpecLoadError

from display import display_result


def main(argv: list[str] | None = None) -> int:
    """CLI エントリポイント。

    Args:
      argv: コマンドライン引数。

    Returns:
      終了コード。
    """
    parser = argparse.ArgumentParser(description="River crossing puzzle solver")
    parser.add_argument(
        "--spec",
        type=Path,
        help="問題定義 YAML のパス",
    )
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="登録済み puzzle_type 一覧を表示",
    )
    parser.add_argument(
        "--tee",
        action="store_true",
        help="ソルバーログを表示",
    )
    args = parser.parse_args(argv)

    if args.list_types:
        for puzzle_type in Engine.list_puzzle_types():
            print(puzzle_type)
        return 0

    if args.spec is None:
        parser.error("--spec is required unless --list-types is given")

    try:
        result = Engine().run(args.spec, tee=args.tee)
    except (SpecLoadError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    display_result(result)
    return 0 if result.status == "optimal" else 2


if __name__ == "__main__":
    raise SystemExit(main())
