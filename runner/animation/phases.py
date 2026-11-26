"""Phase detection for the 4-step cycle and ropeway state."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RopewayMotion(str, Enum):
    """Movement direction or stop position of the ropeway."""

    DOCKED_NEAR = "docked_near"
    DOCKED_FAR = "docked_far"
    TRIP_FORWARD = "trip_forward"
    RETURN_BACK = "return_back"


@dataclass(frozen=True)
class RopewayState:
    """Display state of the ropeway band.

    Attributes:
      motion: Type of motion or stop.
      motion_symbol: Direction symbol on the cable (>> or <<).
      dock_label: Side label when stopped (Near / Far). None while moving.
      is_empty: Whether this is an empty return trip with no passengers.
    """

    motion: RopewayMotion
    motion_symbol: str
    dock_label: str | None
    is_empty: bool


def phase_label(step: int, transit_count: int) -> str:
    """Return the phase label for the header.

    Args:
      step: Time step.
      transit_count: Number of items in transit.

    Returns:
      English phase string.
    """
    if step == 0:
        return "INITIAL"

    mod = step % 4
    if mod == 1:
        return "TRIP ->"
    if mod == 2:
        return "DISEMBARK @ Far"
    if mod == 3:
        if transit_count == 0:
            return "RETURN <- (empty)"
        return "RETURN <-"
    return "DISEMBARK @ Near"


def ropeway_state(step: int, transit_items: tuple[str, ...]) -> RopewayState:
    """Return the display state of the ropeway band.

    Args:
      step: Time step.
      transit_items: Names of items in transit (assumed sorted in items order).

    Returns:
      Ropeway display state.
    """
    if step == 0:
        return RopewayState(
            motion=RopewayMotion.DOCKED_NEAR,
            motion_symbol="",
            dock_label="Near",
            is_empty=True,
        )

    mod = step % 4
    if mod == 1:
        return RopewayState(
            motion=RopewayMotion.TRIP_FORWARD,
            motion_symbol=">>",
            dock_label=None,
            is_empty=len(transit_items) == 0,
        )
    if mod == 2:
        return RopewayState(
            motion=RopewayMotion.DOCKED_FAR,
            motion_symbol="",
            dock_label="Far",
            is_empty=True,
        )
    if mod == 3:
        return RopewayState(
            motion=RopewayMotion.RETURN_BACK,
            motion_symbol="<<",
            dock_label=None,
            is_empty=len(transit_items) == 0,
        )
    return RopewayState(
        motion=RopewayMotion.DOCKED_NEAR,
        motion_symbol="",
        dock_label="Near",
        is_empty=True,
    )
