"""dr_stone 向け制約・目的関数。"""

from __future__ import annotations

from pyomo.environ import (
    Binary,
    ConcreteModel,
    Constraint,
    NonNegativeReals,
    Objective,
    Var,
    minimize,
)

from river_crossing_ip.build_model.indices import ProblemIndices
from river_crossing_ip.types import DrStoneSpec, PuzzleSpec


def add_dr_stone_constraints(
    model: ConcreteModel,
    spec: PuzzleSpec,
    indices: ProblemIndices,
) -> None:
    """dr_stone 固有の制約 C6, C8, C9, C10 を追加する。

    Args:
      model: Pyomo モデル。
      spec: 問題定義。
      indices: インデックス。
    """
    if not isinstance(spec, DrStoneSpec):
        raise TypeError("spec must be DrStoneSpec")

    _add_dr_stone_variables(model)
    _add_c6_weight_capacity(model, spec)
    _add_c8_transit_monitoring(model, spec)
    _add_c9_suspicious_battle_suppression(model, spec)
    _add_c10_suspicious_quasi_battle_suppression(model, spec)


def set_dr_stone_objective(
    model: ConcreteModel,
    spec: PuzzleSpec,
    indices: ProblemIndices,
) -> None:
    """dr_stone の目的関数を設定する。

    minimize T^max - sum(f_t) + 2 + A*eta + B*zeta

    Args:
      model: Pyomo モデル。
      spec: 問題定義。
      indices: インデックス。
    """
    if not isinstance(spec, DrStoneSpec):
        raise TypeError("spec must be DrStoneSpec")

    time_penalty = (
        indices.max_time_step - sum(model.finish_flag[t] for t in model.T) + 2
    )
    model.objective = Objective(
        expr=time_penalty
        + spec.alpha * model.load_ceiling
        + spec.beta * model.total_load,
        sense=minimize,
    )


def _add_dr_stone_variables(model: ConcreteModel) -> None:
    """dr_stone 固有の決定変数を定義する。"""
    model.load_ceiling = Var(domain=NonNegativeReals)
    model.total_load = Var(domain=NonNegativeReals)


def _add_c6_weight_capacity(model: ConcreteModel, spec: DrStoneSpec) -> None:
    """C6-1〜C6-3: 重量定員。"""

    def load_per_move(m: ConcreteModel, time_step: int) -> object:
        return (
            sum(
                spec.item_weights[item] * m.delta_transit[item, time_step]
                for item in m.I
            )
            <= m.load_ceiling
        )

    model.c6_1_load_per_move = Constraint(model.T_odd, rule=load_per_move)

    def load_ceiling_limit(m: ConcreteModel) -> object:
        return m.load_ceiling <= spec.max_load_weight

    model.c6_2_load_ceiling_limit = Constraint(rule=load_ceiling_limit)

    def total_load_definition(m: ConcreteModel) -> object:
        return m.total_load == sum(
            spec.item_weights[item] * m.delta_transit[item, time_step]
            for time_step in m.T_odd
            for item in m.I
        )

    model.c6_3_total_load_definition = Constraint(rule=total_load_definition)


def _add_c8_transit_monitoring(model: ConcreteModel, spec: DrStoneSpec) -> None:
    """C8-1: 移動中の疑いありメンバーの監視。"""
    suspicious = tuple(spec.suspicious_members)
    trusted_battle = tuple(spec.trusted_battle_members)

    def transit_monitoring_rule(m: ConcreteModel, time_step: int) -> object:
        return sum(m.delta_transit[item, time_step] for item in suspicious) <= sum(
            m.delta_transit[item, time_step] for item in trusted_battle
        )

    model.c8_1_transit_monitoring = Constraint(
        model.T_odd,
        rule=transit_monitoring_rule,
    )


def _add_c9_suspicious_battle_suppression(
    model: ConcreteModel,
    spec: DrStoneSpec,
) -> None:
    """C9-1〜C9-6: 疑いありバトルメンバーの抑制。"""
    suspicious_battle = tuple(spec.suspicious_battle_members)
    if not suspicious_battle:
        return

    trusted_battle = tuple(spec.trusted_battle_members)
    num_suspicious_battle = len(suspicious_battle)
    big_m = len(spec.items)

    model.suspicious_battle_present_start = Var(model.T, domain=Binary)
    model.suspicious_battle_present_goal = Var(model.T, domain=Binary)

    def start_presence_lower(m: ConcreteModel, time_step: int) -> object:
        return (
            sum(m.delta_start[item, time_step] for item in suspicious_battle)
            >= m.suspicious_battle_present_start[time_step]
        )

    def start_presence_upper(m: ConcreteModel, time_step: int) -> object:
        return (
            sum(m.delta_start[item, time_step] for item in suspicious_battle)
            <= num_suspicious_battle * m.suspicious_battle_present_start[time_step]
        )

    def goal_presence_lower(m: ConcreteModel, time_step: int) -> object:
        return (
            sum(m.delta_goal[item, time_step] for item in suspicious_battle)
            >= m.suspicious_battle_present_goal[time_step]
        )

    def goal_presence_upper(m: ConcreteModel, time_step: int) -> object:
        return (
            sum(m.delta_goal[item, time_step] for item in suspicious_battle)
            <= num_suspicious_battle * m.suspicious_battle_present_goal[time_step]
        )

    def suppress_start(m: ConcreteModel, time_step: int) -> object:
        suspicious_count = sum(
            m.delta_start[item, time_step] for item in suspicious_battle
        )
        trusted_count = sum(m.delta_start[item, time_step] for item in trusted_battle)
        return suspicious_count + 1 <= trusted_count + big_m * (
            1 - m.suspicious_battle_present_start[time_step]
        )

    def suppress_goal(m: ConcreteModel, time_step: int) -> object:
        suspicious_count = sum(
            m.delta_goal[item, time_step] for item in suspicious_battle
        )
        trusted_count = sum(m.delta_goal[item, time_step] for item in trusted_battle)
        return suspicious_count + 1 <= trusted_count + big_m * (
            1 - m.suspicious_battle_present_goal[time_step]
        )

    model.c9_1_suspicious_battle_start_lower = Constraint(
        model.T,
        rule=start_presence_lower,
    )
    model.c9_2_suspicious_battle_start_upper = Constraint(
        model.T,
        rule=start_presence_upper,
    )
    model.c9_3_suspicious_battle_goal_lower = Constraint(
        model.T,
        rule=goal_presence_lower,
    )
    model.c9_4_suspicious_battle_goal_upper = Constraint(
        model.T,
        rule=goal_presence_upper,
    )
    model.c9_5_battle_suppress_start = Constraint(model.T, rule=suppress_start)
    model.c9_6_battle_suppress_goal = Constraint(model.T, rule=suppress_goal)


def _add_c10_suspicious_quasi_battle_suppression(
    model: ConcreteModel,
    spec: DrStoneSpec,
) -> None:
    """C10-1〜C10-6: 疑いあり准バトルメンバーの抑制。"""
    suspicious_quasi_battle = tuple(spec.suspicious_quasi_battle_members)
    if not suspicious_quasi_battle:
        return

    trusted_quasi_battle = tuple(spec.trusted_quasi_battle_members)
    num_suspicious_quasi_battle = len(suspicious_quasi_battle)
    suppression_margin = 3
    big_m = len(spec.items)

    model.suspicious_quasi_battle_present_start = Var(model.T, domain=Binary)
    model.suspicious_quasi_battle_present_goal = Var(model.T, domain=Binary)

    def start_presence_lower(m: ConcreteModel, time_step: int) -> object:
        return (
            sum(m.delta_start[item, time_step] for item in suspicious_quasi_battle)
            >= m.suspicious_quasi_battle_present_start[time_step]
        )

    def start_presence_upper(m: ConcreteModel, time_step: int) -> object:
        return (
            sum(m.delta_start[item, time_step] for item in suspicious_quasi_battle)
            <= num_suspicious_quasi_battle
            * m.suspicious_quasi_battle_present_start[time_step]
        )

    def goal_presence_lower(m: ConcreteModel, time_step: int) -> object:
        return (
            sum(m.delta_goal[item, time_step] for item in suspicious_quasi_battle)
            >= m.suspicious_quasi_battle_present_goal[time_step]
        )

    def goal_presence_upper(m: ConcreteModel, time_step: int) -> object:
        return (
            sum(m.delta_goal[item, time_step] for item in suspicious_quasi_battle)
            <= num_suspicious_quasi_battle
            * m.suspicious_quasi_battle_present_goal[time_step]
        )

    def suppress_start(m: ConcreteModel, time_step: int) -> object:
        suspicious_count = sum(
            m.delta_start[item, time_step] for item in suspicious_quasi_battle
        )
        trusted_count = sum(
            m.delta_start[item, time_step] for item in trusted_quasi_battle
        )
        return suspicious_count + suppression_margin <= trusted_count + big_m * (
            1 - m.suspicious_quasi_battle_present_start[time_step]
        )

    def suppress_goal(m: ConcreteModel, time_step: int) -> object:
        suspicious_count = sum(
            m.delta_goal[item, time_step] for item in suspicious_quasi_battle
        )
        trusted_count = sum(
            m.delta_goal[item, time_step] for item in trusted_quasi_battle
        )
        return suspicious_count + suppression_margin <= trusted_count + big_m * (
            1 - m.suspicious_quasi_battle_present_goal[time_step]
        )

    model.c10_1_suspicious_quasi_battle_start_lower = Constraint(
        model.T,
        rule=start_presence_lower,
    )
    model.c10_2_suspicious_quasi_battle_start_upper = Constraint(
        model.T,
        rule=start_presence_upper,
    )
    model.c10_3_suspicious_quasi_battle_goal_lower = Constraint(
        model.T,
        rule=goal_presence_lower,
    )
    model.c10_4_suspicious_quasi_battle_goal_upper = Constraint(
        model.T,
        rule=goal_presence_upper,
    )
    model.c10_5_quasi_battle_suppress_start = Constraint(model.T, rule=suppress_start)
    model.c10_6_quasi_battle_suppress_goal = Constraint(model.T, rule=suppress_goal)
