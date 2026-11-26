"""Domain model type definitions for the river crossing puzzle."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GrudgeRule:
    """Grudge rule (one entry of classic forbidden_co_presence).

    Attributes:
      members: Set of items that are dangerous when co-located (H_k in the formulation).
      guardians: Mediators required when members are co-located (G_k in the formulation).
      description: Rule description (optional).
    """

    members: frozenset[str]
    guardians: frozenset[str]
    description: str = ""


@dataclass(frozen=True)
class BaseSpec:
    """Problem definition common to all puzzle_types.

    Attributes:
      puzzle_type: Problem type identifier.
      items: Names of items to move (fixed order, corresponding to index i).
      capacity: Maximum number of items carried in a single move.
      initial_far_side: Items on the goal side from step 0.
      buffer_time: Buffer for horizon computation (T_buffer in the formulation).
    """

    puzzle_type: str
    items: tuple[str, ...]
    capacity: int
    initial_far_side: frozenset[str]
    buffer_time: int


@dataclass(frozen=True)
class ClassicSpec(BaseSpec):
    """Classic problem definition.

    Attributes:
      pilots: Items that can operate the vehicle (P in the formulation).
      forbidden_co_presence: List of grudge rules.
    """

    pilots: frozenset[str] = frozenset()
    forbidden_co_presence: tuple[GrudgeRule, ...] = ()


@dataclass(frozen=True)
class DrStoneSpec(BaseSpec):
    """dr_stone problem definition.

    Attributes:
      item_weights: Weight of each item.
      max_load_weight: Maximum load weight of the vehicle (W^max in the formulation).
      alpha: Penalty coefficient for the load limit eta.
      beta: Penalty coefficient for the total load weight zeta.
      suspicious_members: Suspicious members.
      craft_members: Craft members.
      battle_members: Battle members.
      quasi_battle_members: Quasi-battle members.
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
        """Suspicious craft members (C ∩ S^sus)."""
        return frozenset(self.craft_members & self.suspicious_members)

    @property
    def trusted_craft_members(self) -> frozenset[str]:
        """Non-suspicious craft members (C \\ S^sus)."""
        return frozenset(self.craft_members - self.suspicious_members)

    @property
    def suspicious_battle_members(self) -> frozenset[str]:
        """Suspicious battle members (B ∩ S^sus)."""
        return frozenset(self.battle_members & self.suspicious_members)

    @property
    def trusted_battle_members(self) -> frozenset[str]:
        """Non-suspicious battle members (B \\ S^sus)."""
        return frozenset(self.battle_members - self.suspicious_members)

    @property
    def suspicious_quasi_battle_members(self) -> frozenset[str]:
        """Suspicious quasi-battle members (Q ∩ S^sus)."""
        return frozenset(self.quasi_battle_members & self.suspicious_members)

    @property
    def trusted_quasi_battle_members(self) -> frozenset[str]:
        """Non-suspicious quasi-battle members (Q \\ S^sus)."""
        return frozenset(self.quasi_battle_members - self.suspicious_members)


PuzzleSpec = ClassicSpec | DrStoneSpec
