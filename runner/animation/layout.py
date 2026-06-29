"""ステップごとのエリア配置と移動検出。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from river_crossing_ip.solve.result import Location
from river_crossing_ip.types import DrStoneSpec


class CardStyle(str, Enum):
    """メンバーカードの枠・バッジ種別。"""

    DEFAULT = "default"
    TRUSTED_BATTLE = "trusted_battle"
    SUSP_ONLY = "susp_only"
    SUSP_BATTLE = "susp_battle"


@dataclass(frozen=True)
class StepLayout:
    """1ステップ分の配置情報。

    Attributes:
      near_items: 出発側（Near）にいる対象（items 順）。
      far_items: 到達側（Far）にいる対象（items 順）。
      transit_items: 移動中の対象（items 順）。
      moved_items: 直前ステップから位置が変わった対象。
      load_kg: 移動中の積載重量（kg）。移動中0人のとき None。
    """

    near_items: tuple[str, ...]
    far_items: tuple[str, ...]
    transit_items: tuple[str, ...]
    moved_items: frozenset[str]
    load_kg: int | None


def display_name(item: str) -> str:
    """YAML 内部名を Title Case 表示名に変換する。"""
    return item.title()


def card_style_for_item(item: str, spec: DrStoneSpec) -> CardStyle:
    """対象のカード枠・バッジ種別を返す。

    trusted battle（White）: battle_members かつ suspicious でない。
    SUSP battle: 両方に属する（例: hyoga）。
    SUSP only: suspicious のみ（例: zeno）。

    Args:
      item: 対象名。
      spec: dr_stone 問題定義。

    Returns:
      カードスタイル。
    """
    is_suspicious = item in spec.suspicious_members
    is_battle = item in spec.battle_members
    if is_suspicious and is_battle:
        return CardStyle.SUSP_BATTLE
    if is_suspicious:
        return CardStyle.SUSP_ONLY
    if is_battle:
        return CardStyle.TRUSTED_BATTLE
    return CardStyle.DEFAULT


def items_at_location(
    positions: dict[str, Location],
    location: Location,
    items_order: tuple[str, ...],
) -> tuple[str, ...]:
    """指定位置にいる対象を items 順で返す。"""
    return tuple(item for item in items_order if positions.get(item) == location)


def detect_moved(
    previous: dict[str, Location] | None,
    current: dict[str, Location],
) -> frozenset[str]:
    """直前ステップから位置が変わった対象を返す。"""
    if previous is None:
        return frozenset()
    return frozenset(
        item for item in current if previous.get(item) != current.get(item)
    )


def compute_load_kg(
    transit_items: tuple[str, ...],
    item_weights: dict[str, float],
) -> int | None:
    """移動中乗客の積載重量合計（kg）を返す。"""
    if not transit_items:
        return None
    return int(sum(item_weights[item] for item in transit_items))


def build_step_layout(
    step: int,
    positions: dict[int, dict[str, Location]],
    spec: DrStoneSpec,
) -> StepLayout:
    """1ステップ分の配置情報を構築する。

    Args:
      step: 時間ステップ。
      positions: 全ステップの位置辞書。
      spec: dr_stone 問題定義。

    Returns:
      配置情報。
    """
    current = positions[step]
    previous = positions.get(step - 1)
    transit_items = items_at_location(current, "transit", spec.items)
    return StepLayout(
        near_items=items_at_location(current, "start", spec.items),
        far_items=items_at_location(current, "goal", spec.items),
        transit_items=transit_items,
        moved_items=detect_moved(previous, current),
        load_kg=compute_load_kg(transit_items, spec.item_weights),
    )


def step_duration(
    step: int,
    positions: dict[int, dict[str, Location]],
    *,
    unchanged_seconds: float = 0.5,
    changed_seconds: float = 1.5,
) -> float:
    """ステップの表示秒数を返す。

    Args:
      step: 時間ステップ。
      positions: 全ステップの位置辞書。
      unchanged_seconds: 配置不変時の秒数。
      changed_seconds: 配置変化時の秒数。

    Returns:
      表示秒数。
    """
    if step == 0:
        return changed_seconds
    if positions[step] == positions[step - 1]:
        return unchanged_seconds
    return changed_seconds
