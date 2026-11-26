"""Solver engine for river crossing puzzles."""

from __future__ import annotations

from pathlib import Path

from river_crossing_ip.build_model import build_model, list_puzzle_types
from river_crossing_ip.load_data import load_spec
from river_crossing_ip.solve import SolveResult, solve_model
from river_crossing_ip.types import PuzzleSpec


class Engine:
    """Run the pipeline from YAML loading to solving."""

    def run(
        self,
        spec_path: str | Path,
        *,
        tee: bool = False,
    ) -> SolveResult:
        """Load a problem definition YAML and solve it.

        Args:
          spec_path: Path to the problem definition YAML.
          tee: Whether to show solver logs.

        Returns:
          Solve result.
        """
        spec = load_spec(spec_path)
        return self.run_from_spec(spec, tee=tee)

    def run_from_spec(
        self,
        spec: PuzzleSpec,
        *,
        tee: bool = False,
    ) -> SolveResult:
        """Solve from a problem definition.

        Args:
          spec: Problem definition.
          tee: Whether to show solver logs.

        Returns:
          Solve result.
        """
        model = build_model(spec)
        return solve_model(model, spec, tee=tee)

    @staticmethod
    def list_puzzle_types() -> tuple[str, ...]:
        """Return the list of registered puzzle_types."""
        return list_puzzle_types()
