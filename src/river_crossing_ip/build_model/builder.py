"""Pyomo model construction."""

from __future__ import annotations

from pyomo.environ import ConcreteModel

from river_crossing_ip.build_model.constraints import (
    add_type_constraints,
    set_type_objective,
)
from river_crossing_ip.build_model.constraints.common import (
    add_common_constraints,
    add_common_variables,
)
from river_crossing_ip.build_model.indices import build_indices
from river_crossing_ip.types import PuzzleSpec


class ModelBuilder:
    """Build a Pyomo model from a problem definition."""

    def __init__(self, spec: PuzzleSpec) -> None:
        """Initialize the ModelBuilder.

        Args:
          spec: Problem definition.
        """
        self.spec = spec
        self.indices = build_indices(spec)
        self.model: ConcreteModel | None = None

    def build(self) -> ConcreteModel:
        """Build and return the model.

        Returns:
          Built ConcreteModel.
        """
        self.model = ConcreteModel()
        add_common_variables(self.model, self.spec, self.indices)
        add_common_constraints(self.model, self.spec, self.indices)
        add_type_constraints(self.model, self.spec, self.indices)
        set_type_objective(self.model, self.spec, self.indices)
        return self.model


def build_model(spec: PuzzleSpec) -> ConcreteModel:
    """Build a Pyomo model from a problem definition.

    Args:
      spec: Problem definition.

    Returns:
      Built ConcreteModel.
    """
    return ModelBuilder(spec).build()
