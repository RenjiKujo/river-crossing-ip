"""classic 向け制約・目的関数。"""

from __future__ import annotations

from pyomo.environ import ConcreteModel, Constraint, Objective, minimize

from river_crossing_ip.build_model.indices import ProblemIndices
from river_crossing_ip.types import ClassicSpec, PuzzleSpec


def add_classic_constraints(
    model: ConcreteModel,
    spec: PuzzleSpec,
    indices: ProblemIndices,
) -> None:
    """classic 固有の制約 C6〜C7 を追加する。

    Args:
      model: Pyomo モデル。
      spec: 問題定義。
      indices: インデックス。
    """
    if not isinstance(spec, ClassicSpec):
        raise TypeError("spec must be ClassicSpec")

    _add_c6_grudge_rules(model, spec)
    _add_c7_pilots(model, spec)


def set_classic_objective(
    model: ConcreteModel,
    spec: PuzzleSpec,
    indices: ProblemIndices,
) -> None:
    """classic の目的関数を設定する。

    minimize T^max - sum(f_t) + 2

    Args:
      model: Pyomo モデル。
      spec: 問題定義。
      indices: インデックス。
    """
    model.objective = Objective(
        expr=indices.max_time_step - sum(model.finish_flag[t] for t in model.T) + 2,
        sense=minimize,
    )


def _add_c6_grudge_rules(model: ConcreteModel, spec: ClassicSpec) -> None:
    """C6-1〜C6-3: 遺恨組の仲裁。"""

    for rule_index, rule in enumerate(spec.forbidden_co_presence):
        members = tuple(rule.members)
        guardians = tuple(rule.guardians)
        member_count = len(members)

        def start_rule(
            m: ConcreteModel,
            time_step: int,
            members: tuple[str, ...] = members,
            guardians: tuple[str, ...] = guardians,
            member_count: int = member_count,
        ) -> object:
            return sum(
                m.delta_start[item, time_step] for item in members
            ) - member_count + 1 <= sum(
                m.delta_start[guardian, time_step] for guardian in guardians
            )

        def goal_rule(
            m: ConcreteModel,
            time_step: int,
            members: tuple[str, ...] = members,
            guardians: tuple[str, ...] = guardians,
            member_count: int = member_count,
        ) -> object:
            return sum(
                m.delta_goal[item, time_step] for item in members
            ) - member_count + 1 <= sum(
                m.delta_goal[guardian, time_step] for guardian in guardians
            )

        def transit_rule(
            m: ConcreteModel,
            time_step: int,
            members: tuple[str, ...] = members,
            guardians: tuple[str, ...] = guardians,
            member_count: int = member_count,
        ) -> object:
            return sum(
                m.delta_transit[item, time_step] for item in members
            ) - member_count + 1 <= sum(
                m.delta_transit[guardian, time_step] for guardian in guardians
            )

        model.add_component(
            f"c6_1_grudge_start_{rule_index}",
            Constraint(model.T, rule=start_rule),
        )
        model.add_component(
            f"c6_2_grudge_goal_{rule_index}",
            Constraint(model.T, rule=goal_rule),
        )
        model.add_component(
            f"c6_3_grudge_transit_{rule_index}",
            Constraint(model.T, rule=transit_rule),
        )


def _add_c7_pilots(model: ConcreteModel, spec: ClassicSpec) -> None:
    """C7-1: 操船者。"""

    pilots = tuple(spec.pilots)

    def pilot_rule(m: ConcreteModel, time_step: int) -> object:
        return sum(m.delta_transit[pilot, time_step] for pilot in pilots) >= 1

    model.c7_pilots = Constraint(model.T_odd, rule=pilot_rule)
