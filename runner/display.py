"""求解結果の表示。"""

from __future__ import annotations

from river_crossing_ip.solve.result import SolveResult

LOCATION_LABELS = {
    "start": "出発側",
    "goal": "到達側",
    "transit": "移動中",
}


def display_result(result: SolveResult) -> None:
    """求解結果を標準出力に表示する。

    Args:
      result: 求解結果。
    """
    print(f"status: {result.status}")

    if result.status != "optimal":
        print("求解に失敗しました。")
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
        print(f"  出発側: {', '.join(start_items) if start_items else '-'}")
        if transit_items:
            print(f"  移動中: {', '.join(transit_items)}")
        print(f"  到達側: {', '.join(goal_items) if goal_items else '-'}")


def _items_at(positions: dict[str, str], location: str) -> list[str]:
    """指定位置にいる対象名の一覧を返す。"""
    return sorted(item for item, place in positions.items() if place == location)
