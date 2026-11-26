"""Type definitions for the solve result."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Location = Literal["start", "goal", "transit"]
SolverStatus = Literal["optimal", "infeasible", "unknown"]


@dataclass(frozen=True)
class SolveResult:
    """Solve result.

    Attributes:
      status: Solve status.
      objective_value: Objective value (None if the solve failed).
      finish_step: First step at which everyone is on the goal side (None if the solve failed).
      positions: Position of each item at each step.
    """

    status: SolverStatus
    objective_value: float | None
    finish_step: int | None
    positions: dict[int, dict[str, Location]]
