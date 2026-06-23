"""川渡りパズル求解エンジン。"""

from __future__ import annotations

from pathlib import Path

from river_crossing_ip.build_model import build_model, list_puzzle_types
from river_crossing_ip.load_data import load_spec
from river_crossing_ip.solve import SolveResult, solve_model
from river_crossing_ip.types import PuzzleSpec


class Engine:
    """YAML 読込から求解までのパイプラインを実行する。"""

    def run(
        self,
        spec_path: str | Path,
        *,
        tee: bool = False,
    ) -> SolveResult:
        """問題定義 YAML を読み込み、求解する。

        Args:
          spec_path: 問題定義 YAML のパス。
          tee: ソルバーログを表示するか。

        Returns:
          求解結果。
        """
        spec = load_spec(spec_path)
        return self.run_from_spec(spec, tee=tee)

    def run_from_spec(
        self,
        spec: PuzzleSpec,
        *,
        tee: bool = False,
    ) -> SolveResult:
        """問題定義から求解する。

        Args:
          spec: 問題定義。
          tee: ソルバーログを表示するか。

        Returns:
          求解結果。
        """
        model = build_model(spec)
        return solve_model(model, spec, tee=tee)

    @staticmethod
    def list_puzzle_types() -> tuple[str, ...]:
        """登録済み puzzle_type 一覧を返す。"""
        return list_puzzle_types()
