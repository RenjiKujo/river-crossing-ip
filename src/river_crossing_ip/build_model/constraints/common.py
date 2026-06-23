"""共通制約（common.md）。"""

from __future__ import annotations

from pyomo.environ import Binary, ConcreteModel, Constraint, Set, Var

from river_crossing_ip.build_model.indices import ProblemIndices
from river_crossing_ip.types import PuzzleSpec


def add_common_variables(
    model: ConcreteModel,
    spec: PuzzleSpec,
    indices: ProblemIndices,
) -> None:
    """共通決定変数を定義する。

    Args:
      model: Pyomo モデル。
      spec: 問題定義。
      indices: インデックス。
    """
    model.spec = spec
    model.indices = indices
    model.num_items = len(indices.items)

    model.I = Set(initialize=indices.items)
    model.T = Set(initialize=indices.time_steps)
    model.T_even = Set(initialize=indices.even_time_steps)
    model.T_odd = Set(initialize=indices.odd_time_steps)
    model.T_4n1 = Set(initialize=indices.time_steps_4n_plus_1)
    model.T_4n3 = Set(initialize=indices.time_steps_4n_plus_3)

    model.delta_start = Var(model.I, model.T, domain=Binary)
    model.delta_goal = Var(model.I, model.T, domain=Binary)
    model.delta_transit = Var(model.I, model.T, domain=Binary)
    model.finish_flag = Var(model.T, domain=Binary)


def add_common_constraints(
    model: ConcreteModel,
    spec: PuzzleSpec,
    indices: ProblemIndices,
) -> None:
    """common.md の共通制約 C1〜C5 を追加する。

    Args:
      model: Pyomo モデル。
      spec: 問題定義。
      indices: インデックス。
    """
    _add_c1_location_uniqueness(model)
    _add_c2_state_transition(model)
    _add_c3_initial_state(model, indices)
    _add_c4_finish_flag(model, indices)
    _add_c5_capacity(model, indices)


def _add_c1_location_uniqueness(model: ConcreteModel) -> None:
    """C1-1: 各対象は各ステップでちょうど1地点に存在する。"""

    def rule(m: ConcreteModel, item: str, time_step: int) -> object:
        return (
            m.delta_start[item, time_step]
            + m.delta_goal[item, time_step]
            + m.delta_transit[item, time_step]
            == 1
        )

    model.c1_location_uniqueness = Constraint(model.I, model.T, rule=rule)


def _add_c2_state_transition(model: ConcreteModel) -> None:
    """C2-1〜C2-15: 偶数・奇数ステップの状態遷移。"""

    def no_transit_on_even(m: ConcreteModel, item: str, time_step: int) -> object:
        return m.delta_transit[item, time_step] == 0

    model.c2_1_no_transit_on_even = Constraint(
        model.I, model.T_even, rule=no_transit_on_even
    )

    def forward_upper_start(m: ConcreteModel, item: str, time_step: int) -> object:
        return m.delta_transit[item, time_step] <= m.delta_start[item, time_step - 1]

    def forward_upper_goal(m: ConcreteModel, item: str, time_step: int) -> object:
        return m.delta_transit[item, time_step] <= m.delta_goal[item, time_step + 1]

    def forward_lower(m: ConcreteModel, item: str, time_step: int) -> object:
        return (
            m.delta_transit[item, time_step]
            >= m.delta_start[item, time_step - 1]
            + m.delta_goal[item, time_step + 1]
            - 1
        )

    model.c2_2_forward_upper_start = Constraint(
        model.I, model.T_4n1, rule=forward_upper_start
    )
    model.c2_3_forward_upper_goal = Constraint(
        model.I, model.T_4n1, rule=forward_upper_goal
    )
    model.c2_4_forward_lower = Constraint(model.I, model.T_4n1, rule=forward_lower)

    def backward_upper_goal(m: ConcreteModel, item: str, time_step: int) -> object:
        return m.delta_transit[item, time_step] <= m.delta_goal[item, time_step - 1]

    def backward_upper_start(m: ConcreteModel, item: str, time_step: int) -> object:
        return m.delta_transit[item, time_step] <= m.delta_start[item, time_step + 1]

    def backward_lower(m: ConcreteModel, item: str, time_step: int) -> object:
        return (
            m.delta_transit[item, time_step]
            >= m.delta_goal[item, time_step - 1]
            + m.delta_start[item, time_step + 1]
            - 1
        )

    model.c2_5_backward_upper_goal = Constraint(
        model.I, model.T_4n3, rule=backward_upper_goal
    )
    model.c2_6_backward_upper_start = Constraint(
        model.I, model.T_4n3, rule=backward_upper_start
    )
    model.c2_7_backward_lower = Constraint(model.I, model.T_4n3, rule=backward_lower)

    def c2_8(m: ConcreteModel, item: str, time_step: int) -> object:
        return (
            m.delta_start[item, time_step - 1] - m.delta_start[item, time_step]
            <= m.delta_transit[item, time_step]
        )

    def c2_9(m: ConcreteModel, item: str, time_step: int) -> object:
        return (
            m.delta_start[item, time_step] - m.delta_start[item, time_step - 1]
            <= m.delta_transit[item, time_step]
        )

    def c2_10(m: ConcreteModel, item: str, time_step: int) -> object:
        return (
            m.delta_start[item, time_step] - m.delta_start[item, time_step + 1]
            <= m.delta_transit[item, time_step]
        )

    def c2_11(m: ConcreteModel, item: str, time_step: int) -> object:
        return (
            m.delta_start[item, time_step + 1] - m.delta_start[item, time_step]
            <= m.delta_transit[item, time_step]
        )

    def c2_12(m: ConcreteModel, item: str, time_step: int) -> object:
        return (
            m.delta_goal[item, time_step - 1] - m.delta_goal[item, time_step]
            <= m.delta_transit[item, time_step]
        )

    def c2_13(m: ConcreteModel, item: str, time_step: int) -> object:
        return (
            m.delta_goal[item, time_step] - m.delta_goal[item, time_step - 1]
            <= m.delta_transit[item, time_step]
        )

    def c2_14(m: ConcreteModel, item: str, time_step: int) -> object:
        return (
            m.delta_goal[item, time_step] - m.delta_goal[item, time_step + 1]
            <= m.delta_transit[item, time_step]
        )

    def c2_15(m: ConcreteModel, item: str, time_step: int) -> object:
        return (
            m.delta_goal[item, time_step + 1] - m.delta_goal[item, time_step]
            <= m.delta_transit[item, time_step]
        )

    model.c2_8_start_prev = Constraint(model.I, model.T_odd, rule=c2_8)
    model.c2_9_start_next_prev = Constraint(model.I, model.T_odd, rule=c2_9)
    model.c2_10_start_next = Constraint(model.I, model.T_odd, rule=c2_10)
    model.c2_11_start_next_rev = Constraint(model.I, model.T_odd, rule=c2_11)
    model.c2_12_goal_prev = Constraint(model.I, model.T_odd, rule=c2_12)
    model.c2_13_goal_next_prev = Constraint(model.I, model.T_odd, rule=c2_13)
    model.c2_14_goal_next = Constraint(model.I, model.T_odd, rule=c2_14)
    model.c2_15_goal_next_rev = Constraint(model.I, model.T_odd, rule=c2_15)


def _add_c3_initial_state(model: ConcreteModel, indices: ProblemIndices) -> None:
    """C3-1〜C3-2: ステップ0の初期配置。"""

    def on_far_side(m: ConcreteModel, item: str) -> object:
        return m.delta_goal[item, 0] == 1

    def not_on_far_side(m: ConcreteModel, item: str) -> object:
        return m.delta_goal[item, 0] == 0

    if indices.initial_far_side_items:
        model.c3_1_initial_far_side = Constraint(
            list(indices.initial_far_side_items),
            rule=on_far_side,
        )

    near_side_items = [
        item for item in indices.items if item not in indices.initial_far_side_items
    ]
    if near_side_items:
        model.c3_2_initial_near_side = Constraint(
            near_side_items,
            rule=not_on_far_side,
        )


def _add_c4_finish_flag(model: ConcreteModel, indices: ProblemIndices) -> None:
    """C4-1〜C4-4: フィニッシュフラグ。"""

    def finish_implies_all_goal(m: ConcreteModel, item: str, time_step: int) -> object:
        return m.finish_flag[time_step] <= m.delta_goal[item, time_step]

    model.c4_1_finish_implies_all_goal = Constraint(
        model.I,
        model.T,
        rule=finish_implies_all_goal,
    )

    def all_goal_implies_finish(m: ConcreteModel, time_step: int) -> object:
        return m.finish_flag[time_step] >= 1 - m.num_items + sum(
            m.delta_goal[item, time_step] for item in m.I
        )

    model.c4_2_all_goal_implies_finish = Constraint(
        model.T, rule=all_goal_implies_finish
    )

    finish_transition_steps = tuple(range(indices.max_time_step))
    model.T_finish_transition = Set(initialize=finish_transition_steps)

    def finish_monotone(m: ConcreteModel, time_step: int) -> object:
        return m.finish_flag[time_step] <= m.finish_flag[time_step + 1]

    model.c4_3_finish_monotone = Constraint(
        model.T_finish_transition,
        rule=finish_monotone,
    )

    def must_finish(m: ConcreteModel) -> object:
        return m.finish_flag[indices.max_time_step] == 1

    model.c4_4_must_finish = Constraint(rule=must_finish)


def _add_c5_capacity(model: ConcreteModel, indices: ProblemIndices) -> None:
    """C5-1: 移動中の人数定員。"""

    def capacity_rule(m: ConcreteModel, time_step: int) -> object:
        return sum(m.delta_transit[item, time_step] for item in m.I) <= indices.capacity

    model.c5_capacity = Constraint(model.T_odd, rule=capacity_rule)
