"""Display of the solve result."""

from __future__ import annotations

from river_crossing_ip.solve.result import SolveResult

LOCATION_LABELS = {
    "start": "Start side",
    "goal": "Goal side",
    "transit": "In transit",
}


def display_result(result: SolveResult) -> None:
    """Print the solve result to standard output.

    Args:
      result: Solve result.
    """
    print(f"status: {result.status}")

    if result.status != "optimal":
        print("Solve failed.")
        return

    print(f"objective: {result.objective_value}")
    print(f"finish_step: {result.finish_step}")

    if result.finish_step is None:
        return

    for time_step in range(result.finish_step + 1):
        positions = result.positions[time_step]
        start_items = _items_at(positions, "start")
        goal_items = _items_at(positions, "goal")
        transit_items = _items_at(positions, "transit")

        print(f"\nstep {time_step}")
        print(f"  Start side: {', '.join(start_items) if start_items else '-'}")
        if transit_items:
            print(f"  In transit: {', '.join(transit_items)}")
        print(f"  Goal side: {', '.join(goal_items) if goal_items else '-'}")


def _items_at(positions: dict[str, str], location: str) -> list[str]:
    """Return the names of items at the given position."""
    return sorted(item for item, place in positions.items() if place == location)
