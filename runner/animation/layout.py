"""Per-step area placement and movement detection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from river_crossing_ip.solve.result import Location
from river_crossing_ip.types import ClassicSpec, DrStoneSpec, PuzzleSpec


class CardStyle(str, Enum):
    """Frame and badge type of a member card."""

    DEFAULT = "default"
    PILOT = "pilot"
    TRUSTED_BATTLE = "trusted_battle"
    SUSP_ONLY = "susp_only"
    SUSP_BATTLE = "susp_battle"


@dataclass(frozen=True)
class StepLayout:
    """Placement info for one step.

    Attributes:
      near_items: Items on the start side (Near), in items order.
      far_items: Items on the goal side (Far), in items order.
      transit_items: Items in transit, in items order.
      moved_items: Items whose position changed since the previous step.
      load_kg: Load weight in transit (kg). None for classic or when no one is in transit.
    """

    near_items: tuple[str, ...]
    far_items: tuple[str, ...]
    transit_items: tuple[str, ...]
    moved_items: frozenset[str]
    load_kg: int | None


def display_name(item: str) -> str:
    """Convert an internal YAML name into a Title Case display name."""
    return item.title()


def card_style_for_item(item: str, spec: PuzzleSpec) -> CardStyle:
    """Return the card frame and badge type of an item.

    classic: items in pilots are PILOT.
    dr_stone:
      trusted battle (White): in battle_members and not suspicious.
      SUSP battle: belongs to both (e.g. hyoga).
      SUSP only: suspicious only (e.g. zeno).

    Args:
      item: Item name.
      spec: Problem definition.

    Returns:
      Card style.
    """
    if isinstance(spec, ClassicSpec):
        if item in spec.pilots:
            return CardStyle.PILOT
        return CardStyle.DEFAULT

    is_suspicious = item in spec.suspicious_members
    is_battle = item in spec.battle_members
    if is_suspicious and is_battle:
        return CardStyle.SUSP_BATTLE
    if is_suspicious:
        return CardStyle.SUSP_ONLY
    if is_battle:
        return CardStyle.TRUSTED_BATTLE
    return CardStyle.DEFAULT


def items_at_location(
    positions: dict[str, Location],
    location: Location,
    items_order: tuple[str, ...],
) -> tuple[str, ...]:
    """Return the items at the given position in items order."""
    return tuple(item for item in items_order if positions.get(item) == location)


def detect_moved(
    previous: dict[str, Location] | None,
    current: dict[str, Location],
) -> frozenset[str]:
    """Return the items whose position changed since the previous step."""
    if previous is None:
        return frozenset()
    return frozenset(
        item for item in current if previous.get(item) != current.get(item)
    )


def compute_load_kg(
    transit_items: tuple[str, ...],
    item_weights: dict[str, float],
) -> int | None:
    """Return the total load weight (kg) of passengers in transit."""
    if not transit_items:
        return None
    return int(sum(item_weights[item] for item in transit_items))


def build_step_layout(
    step: int,
    positions: dict[int, dict[str, Location]],
    spec: PuzzleSpec,
) -> StepLayout:
    """Build the placement info for one step.

    Args:
      step: Time step.
      positions: Position dictionary for all steps.
      spec: Problem definition.

    Returns:
      Placement info.
    """
    current = positions[step]
    previous = positions.get(step - 1)
    transit_items = items_at_location(current, "transit", spec.items)
    load_kg: int | None = None
    if isinstance(spec, DrStoneSpec):
        load_kg = compute_load_kg(transit_items, spec.item_weights)
    return StepLayout(
        near_items=items_at_location(current, "start", spec.items),
        far_items=items_at_location(current, "goal", spec.items),
        transit_items=transit_items,
        moved_items=detect_moved(previous, current),
        load_kg=load_kg,
    )


def step_duration(
    step: int,
    positions: dict[int, dict[str, Location]],
    *,
    unchanged_seconds: float = 0.6,
    changed_seconds: float = 2.0,
) -> float:
    """Return the display duration of a step in seconds.

    Args:
      step: Time step.
      positions: Position dictionary for all steps.
      unchanged_seconds: Seconds when the placement is unchanged.
      changed_seconds: Seconds when the placement changes.

    Returns:
      Display duration in seconds.
    """
    if step == 0:
        return changed_seconds
    if positions[step] == positions[step - 1]:
        return unchanged_seconds
    return changed_seconds
