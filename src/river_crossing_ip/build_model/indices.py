"""時間ステップ集合とインデックスの導出。"""

from __future__ import annotations

import math
from dataclasses import dataclass

from river_crossing_ip.types import BaseSpec, PuzzleSpec


@dataclass(frozen=True)
class ProblemIndices:
    """定式化で用いるインデックス・集合のまとめ。

    Attributes:
      items: 移動対象名（順序固定）。
      item_to_index: 対象名からインデックスへの写像。
      max_time_step: 最大時間ステップ T^max。
      time_steps: 時間ステップ集合 T。
      even_time_steps: 偶数ステップ集合 T^even。
      odd_time_steps: 奇数ステップ集合 T^odd。
      time_steps_4n_plus_1: 出発側→到達側移動ステップ集合。
      time_steps_4n_plus_3: 到達側→出発側移動ステップ集合。
      capacity: 最大積載人数 C。
      initial_far_side_items: ステップ0の到達側対象 I_0^goal。
      buffer_time: ホライゾンバッファ T^buffer。
    """

    items: tuple[str, ...]
    item_to_index: dict[str, int]
    max_time_step: int
    time_steps: tuple[int, ...]
    even_time_steps: tuple[int, ...]
    odd_time_steps: tuple[int, ...]
    time_steps_4n_plus_1: tuple[int, ...]
    time_steps_4n_plus_3: tuple[int, ...]
    capacity: int
    initial_far_side_items: frozenset[str]
    buffer_time: int


def compute_max_time_step(
    num_items: int,
    capacity: int,
    buffer_time: int,
) -> int:
    """最大時間ステップ T^max を計算する。

    T^max = 4 * (ceil(|I| / C) + T^buffer) + 2

    Args:
      num_items: 対象数 |I|。
      capacity: 最大積載人数 C。
      buffer_time: バッファ T^buffer。

    Returns:
      最大時間ステップ。
    """
    if num_items < 0:
        raise ValueError(f"num_items must be non-negative, got {num_items}")
    if capacity < 1:
        raise ValueError(f"capacity must be at least 1, got {capacity}")
    if buffer_time < 0:
        raise ValueError(f"buffer_time must be non-negative, got {buffer_time}")

    return 4 * (math.ceil(num_items / capacity) + buffer_time) + 2


def build_time_steps(max_time_step: int) -> tuple[int, ...]:
    """時間ステップ集合 T = {0, ..., T^max} を返す。"""
    return tuple(range(max_time_step + 1))


def build_even_time_steps(max_time_step: int) -> tuple[int, ...]:
    """偶数ステップ集合 T^even = {0, 2, 4, ..., T^max} を返す。"""
    return tuple(range(0, max_time_step + 1, 2))


def build_odd_time_steps(max_time_step: int) -> tuple[int, ...]:
    """奇数ステップ集合 T^odd = {1, 3, ..., T^max - 1} を返す。"""
    return tuple(range(1, max_time_step, 2))


def build_time_steps_4n_plus_1(max_time_step: int) -> tuple[int, ...]:
    """出発側→到達側移動ステップ集合 T^{4n+1} を返す。"""
    return tuple(range(1, max_time_step, 4))


def build_time_steps_4n_plus_3(max_time_step: int) -> tuple[int, ...]:
    """到達側→出発側移動ステップ集合 T^{4n+3} を返す。"""
    return tuple(range(3, max_time_step - 2, 4))


def build_indices(spec: PuzzleSpec | BaseSpec) -> ProblemIndices:
    """問題定義からインデックス・集合を構築する。

    Args:
      spec: 問題定義。

    Returns:
      定式化用インデックス。
    """
    max_time_step = compute_max_time_step(
        num_items=len(spec.items),
        capacity=spec.capacity,
        buffer_time=spec.buffer_time,
    )
    return ProblemIndices(
        items=spec.items,
        item_to_index={name: index for index, name in enumerate(spec.items)},
        max_time_step=max_time_step,
        time_steps=build_time_steps(max_time_step),
        even_time_steps=build_even_time_steps(max_time_step),
        odd_time_steps=build_odd_time_steps(max_time_step),
        time_steps_4n_plus_1=build_time_steps_4n_plus_1(max_time_step),
        time_steps_4n_plus_3=build_time_steps_4n_plus_3(max_time_step),
        capacity=spec.capacity,
        initial_far_side_items=spec.initial_far_side,
        buffer_time=spec.buffer_time,
    )
