"""4ステップ周期のフェーズ判定とロープウェー状態。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RopewayMotion(str, Enum):
    """ロープウェーの移動方向または停車位置。"""

    DOCKED_NEAR = "docked_near"
    DOCKED_FAR = "docked_far"
    TRIP_FORWARD = "trip_forward"
    RETURN_BACK = "return_back"


@dataclass(frozen=True)
class RopewayState:
    """ロープウェー帯の表示状態。

    Attributes:
      motion: 移動・停車の種別。
      motion_symbol: ケーブル上の方向記号（>> または <<）。
      dock_label: 停車時の側ラベル（Near / Far）。移動中は None。
      is_empty: 乗客なしの帰り移動かどうか。
    """

    motion: RopewayMotion
    motion_symbol: str
    dock_label: str | None
    is_empty: bool


def phase_label(step: int, transit_count: int) -> str:
    """ヘッダー用フェーズラベルを返す。

    Args:
      step: 時間ステップ。
      transit_count: 移動中の人数。

    Returns:
      英語フェーズ文字列。
    """
    if step == 0:
        return "INITIAL"

    mod = step % 4
    if mod == 1:
        return "TRIP ->"
    if mod == 2:
        return "DISEMBARK @ Far"
    if mod == 3:
        if transit_count == 0:
            return "RETURN <- (empty)"
        return "RETURN <-"
    return "DISEMBARK @ Near"


def ropeway_state(step: int, transit_items: tuple[str, ...]) -> RopewayState:
    """ロープウェー帯の表示状態を返す。

    Args:
      step: 時間ステップ。
      transit_items: 移動中の対象名（items 順でソート済み想定）。

    Returns:
      ロープウェー表示状態。
    """
    if step == 0:
        return RopewayState(
            motion=RopewayMotion.DOCKED_NEAR,
            motion_symbol="",
            dock_label="Near",
            is_empty=True,
        )

    mod = step % 4
    if mod == 1:
        return RopewayState(
            motion=RopewayMotion.TRIP_FORWARD,
            motion_symbol=">>",
            dock_label=None,
            is_empty=len(transit_items) == 0,
        )
    if mod == 2:
        return RopewayState(
            motion=RopewayMotion.DOCKED_FAR,
            motion_symbol="",
            dock_label="Far",
            is_empty=True,
        )
    if mod == 3:
        return RopewayState(
            motion=RopewayMotion.RETURN_BACK,
            motion_symbol="<<",
            dock_label=None,
            is_empty=len(transit_items) == 0,
        )
    return RopewayState(
        motion=RopewayMotion.DOCKED_NEAR,
        motion_symbol="",
        dock_label="Near",
        is_empty=True,
    )
