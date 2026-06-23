"""puzzle_type ごとの制約・目的関数ディスパッチ。"""

from __future__ import annotations

from collections.abc import Callable

from pyomo.environ import ConcreteModel

from river_crossing_ip.build_model.constraints.classic import (
    add_classic_constraints,
    set_classic_objective,
)
from river_crossing_ip.build_model.constraints.dr_stone import (
    add_dr_stone_constraints,
    set_dr_stone_objective,
)
from river_crossing_ip.build_model.indices import ProblemIndices
from river_crossing_ip.types import PuzzleSpec

ConstraintHandler = Callable[[ConcreteModel, PuzzleSpec, ProblemIndices], None]
ObjectiveHandler = Callable[[ConcreteModel, PuzzleSpec, ProblemIndices], None]

TYPE_HANDLERS: dict[str, tuple[ConstraintHandler, ObjectiveHandler]] = {
    "classic": (add_classic_constraints, set_classic_objective),
    "dr_stone": (add_dr_stone_constraints, set_dr_stone_objective),
}


def list_puzzle_types() -> tuple[str, ...]:
    """登録済み puzzle_type 一覧を返す。"""
    return tuple(sorted(TYPE_HANDLERS))


def add_type_constraints(
    model: ConcreteModel,
    spec: PuzzleSpec,
    indices: ProblemIndices,
) -> None:
    """puzzle_type 固有の制約を追加する。"""
    handler, _ = _get_handlers(spec.puzzle_type)
    handler(model, spec, indices)


def set_type_objective(
    model: ConcreteModel,
    spec: PuzzleSpec,
    indices: ProblemIndices,
) -> None:
    """puzzle_type 固有の目的関数を設定する。"""
    _, handler = _get_handlers(spec.puzzle_type)
    handler(model, spec, indices)


def _get_handlers(puzzle_type: str) -> tuple[ConstraintHandler, ObjectiveHandler]:
    """puzzle_type に対応するハンドラを返す。"""
    try:
        return TYPE_HANDLERS[puzzle_type]
    except KeyError as exc:
        raise ValueError(f"unsupported puzzle_type: {puzzle_type!r}") from exc
