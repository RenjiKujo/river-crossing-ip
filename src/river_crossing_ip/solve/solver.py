"""Solving with HiGHS."""

from __future__ import annotations

from pyomo.environ import ConcreteModel, SolverFactory, TerminationCondition, value

from river_crossing_ip.solve.result import Location, SolveResult, SolverStatus
from river_crossing_ip.types import PuzzleSpec


def solve_model(
    model: ConcreteModel,
    spec: PuzzleSpec,
    *,
    tee: bool = False,
) -> SolveResult:
    """Solve a Pyomo model with HiGHS.

    Args:
      model: Model to solve.
      spec: Problem definition.
      tee: Whether to show solver logs.

    Returns:
      Solve result.
    """
    solver = SolverFactory("appsi_highs")
    results = solver.solve(model, tee=tee, load_solutions=False)
    termination = results.solver.termination_condition

    if termination == TerminationCondition.optimal:
        model.solutions.load_from(results)
        return _build_optimal_result(model, spec)

    if termination == TerminationCondition.infeasible:
        return _empty_result("infeasible")

    return _empty_result("unknown")


def _empty_result(status: SolverStatus) -> SolveResult:
    """Return an empty result on failure."""
    return SolveResult(
        status=status,
        objective_value=None,
        finish_step=None,
        positions={},
    )


def _build_optimal_result(model: ConcreteModel, spec: PuzzleSpec) -> SolveResult:
    """Build a SolveResult from the optimal solution."""
    positions = _extract_positions(model, spec)
    finish_step = _extract_finish_step(model)
    objective_value = float(value(model.objective))

    return SolveResult(
        status="optimal",
        objective_value=objective_value,
        finish_step=finish_step,
        positions=positions,
    )


def _extract_finish_step(model: ConcreteModel) -> int | None:
    """Return the first step at which everyone has finished."""
    for time_step in sorted(model.T):
        if _binary_value(model.finish_flag[time_step]) == 1:
            return int(time_step)
    return None


def _extract_positions(
    model: ConcreteModel,
    spec: PuzzleSpec,
) -> dict[int, dict[str, Location]]:
    """Extract the placement at each step."""
    positions: dict[int, dict[str, Location]] = {}
    for time_step in model.T:
        step_positions: dict[str, Location] = {}
        for item in spec.items:
            if _binary_value(model.delta_start[item, time_step]) == 1:
                step_positions[item] = "start"
            elif _binary_value(model.delta_goal[item, time_step]) == 1:
                step_positions[item] = "goal"
            else:
                step_positions[item] = "transit"
        positions[int(time_step)] = step_positions
    return positions


def _binary_value(var: object) -> int:
    """Round a binary variable value to 0/1."""
    numeric = value(var)
    if numeric is None:
        return 0
    return 1 if numeric > 0.5 else 0
