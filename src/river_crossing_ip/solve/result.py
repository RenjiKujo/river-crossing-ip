"""求解結果の型定義。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Location = Literal["start", "goal", "transit"]
SolverStatus = Literal["optimal", "infeasible", "unknown"]


@dataclass(frozen=True)
class SolveResult:
    """求解結果。

    Attributes:
      status: 求解ステータス。
      objective_value: 目的関数値（求解失敗時は None）。
      finish_step: 全員が到達側にいる最初のステップ（求解失敗時は None）。
      positions: 各ステップ・各対象の位置。
    """

    status: SolverStatus
    objective_value: float | None
    finish_step: int | None
    positions: dict[int, dict[str, Location]]
