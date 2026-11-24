#!/usr/bin/env python3
"""求解結果アニメーション mp4 生成 CLI。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from river_crossing_ip.engine import Engine
from river_crossing_ip.load_data import SpecLoadError, load_spec
from river_crossing_ip.types import ClassicSpec, DrStoneSpec, PuzzleSpec

from animation.draw import create_canvas
from animation.export import export_mp4

SUPPORTED_SPECS = (ClassicSpec, DrStoneSpec)


def main(argv: list[str] | None = None) -> int:
    """CLI エントリポイント。

    Args:
      argv: コマンドライン引数。

    Returns:
      終了コード。
    """
    parser = argparse.ArgumentParser(
        description=(
            "Export classic / dr_stone solve result as a short-form mp4 animation"
        ),
    )
    parser.add_argument(
        "--spec",
        type=Path,
        required=True,
        help="Problem spec YAML path (classic or dr_stone)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output mp4 path (default: out/{puzzle_type}_short.mp4)",
    )
    parser.add_argument(
        "--intro-seconds",
        type=float,
        default=1.0,
        help="Intro frame duration in seconds",
    )
    parser.add_argument(
        "--no-intro",
        action="store_true",
        help="Skip intro frame",
    )
    parser.add_argument(
        "--tee",
        action="store_true",
        help="Show solver log",
    )
    args = parser.parse_args(argv)

    try:
        spec = load_spec(args.spec)
    except (SpecLoadError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not isinstance(spec, SUPPORTED_SPECS):
        print(
            "error: animation supports puzzle_type=classic or dr_stone only",
            file=sys.stderr,
        )
        return 1

    output_path = args.output
    if output_path is None:
        output_path = Path("out") / f"{spec.puzzle_type}_short.mp4"

    return _export_animation(
        spec,
        output_path,
        intro_seconds=args.intro_seconds,
        include_intro=not args.no_intro,
        tee=args.tee,
    )


def _export_animation(
    spec: PuzzleSpec,
    output_path: Path,
    *,
    intro_seconds: float,
    include_intro: bool,
    tee: bool,
) -> int:
    """求解して mp4 を書き出す。"""
    try:
        result = Engine().run_from_spec(spec, tee=tee)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if result.status != "optimal":
        print(f"error: solve status is {result.status!r}, not optimal", file=sys.stderr)
        return 2

    figure, axes = create_canvas()
    try:
        export_mp4(
            figure,
            axes,
            result,
            spec,
            output_path,
            intro_seconds=intro_seconds,
            include_intro=include_intro,
        )
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        import matplotlib.pyplot as plt

        plt.close(figure)

    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
