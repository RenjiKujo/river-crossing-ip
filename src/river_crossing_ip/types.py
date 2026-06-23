"""川渡りパズルのドメインモデル型定義。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GrudgeRule:
    """遺恨ルール（classic の forbidden_co_presence 1件分）。

    Attributes:
      members: 同地点にいると危険な対象の集合（定式化の H_k）。
      guardians: members が同地点にいるとき必要な仲裁対象（定式化の G_k）。
      description: ルールの説明（任意）。
    """

    members: frozenset[str]
    guardians: frozenset[str]
    description: str = ""


@dataclass(frozen=True)
class BaseSpec:
    """puzzle_type 共通の問題定義。

    Attributes:
      puzzle_type: 問題タイプ識別子。
      items: 移動対象の名前（順序固定でインデックス i に対応）。
      capacity: 1回の移動で同時に運べる最大人数。
      initial_far_side: ステップ0から到達側にいる対象。
      buffer_time: ホライゾン計算用バッファ（定式化の T_buffer）。
    """

    puzzle_type: str
    items: tuple[str, ...]
    capacity: int
    initial_far_side: frozenset[str]
    buffer_time: int


@dataclass(frozen=True)
class ClassicSpec(BaseSpec):
    """classic 問題定義。

    Attributes:
      pilots: 輸送手段を操縦できる対象（定式化の P）。
      forbidden_co_presence: 遺恨ルールの一覧。
    """

    pilots: frozenset[str] = frozenset()
    forbidden_co_presence: tuple[GrudgeRule, ...] = ()


@dataclass(frozen=True)
class DrStoneSpec(BaseSpec):
    """dr_stone 問題定義。

    Attributes:
      item_weights: 対象ごとの重量。
      max_load_weight: 輸送手段の最大積載重量（定式化の W^max）。
      alpha: 積載上限 eta のペナルティ係数。
      beta: 積載重量合計 zeta のペナルティ係数。
      suspicious_members: 疑いありメンバー。
      craft_members: クラフトメンバー。
      battle_members: バトルメンバー。
      quasi_battle_members: 准バトルメンバー。
    """

    item_weights: dict[str, float]
    max_load_weight: float
    alpha: float = 0.0
    beta: float = 0.0
    suspicious_members: frozenset[str] = frozenset()
    craft_members: frozenset[str] = frozenset()
    battle_members: frozenset[str] = frozenset()
    quasi_battle_members: frozenset[str] = frozenset()

    @property
    def suspicious_craft_members(self) -> frozenset[str]:
        """疑いありクラフトメンバー（C ∩ S^sus）。"""
        return frozenset(self.craft_members & self.suspicious_members)

    @property
    def trusted_craft_members(self) -> frozenset[str]:
        """疑いなしクラフトメンバー（C \\ S^sus）。"""
        return frozenset(self.craft_members - self.suspicious_members)

    @property
    def suspicious_battle_members(self) -> frozenset[str]:
        """疑いありバトルメンバー（B ∩ S^sus）。"""
        return frozenset(self.battle_members & self.suspicious_members)

    @property
    def trusted_battle_members(self) -> frozenset[str]:
        """疑いなしバトルメンバー（B \\ S^sus）。"""
        return frozenset(self.battle_members - self.suspicious_members)

    @property
    def suspicious_quasi_battle_members(self) -> frozenset[str]:
        """疑いあり准バトルメンバー（Q ∩ S^sus）。"""
        return frozenset(self.quasi_battle_members & self.suspicious_members)

    @property
    def trusted_quasi_battle_members(self) -> frozenset[str]:
        """疑いなし准バトルメンバー（Q \\ S^sus）。"""
        return frozenset(self.quasi_battle_members - self.suspicious_members)


PuzzleSpec = ClassicSpec | DrStoneSpec
