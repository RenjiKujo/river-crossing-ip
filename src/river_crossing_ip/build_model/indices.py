"""Derivation of time step sets and indices."""

from __future__ import annotations

import math
from dataclasses import dataclass

from river_crossing_ip.types import BaseSpec, PuzzleSpec


@dataclass(frozen=True)
class ProblemIndices:
    """Summary of indices and sets used in the formulation.

    Attributes:
      items: Names of items to move (fixed order).
      item_to_index: Mapping from item name to index.
      max_time_step: Maximum time step T^max.
      time_steps: Time step set T.
      even_time_steps: Even step set T^even.
      odd_time_steps: Odd step set T^odd.
      time_steps_4n_plus_1: Set of start-to-goal move steps.
      time_steps_4n_plus_3: Set of goal-to-start move steps.
      capacity: Maximum number of items per load C.
      initial_far_side_items: Items on the goal side at step 0, I_0^goal.
      buffer_time: Horizon buffer T^buffer.
    """

    items: tuple[str, ...]
    item_to_index: dict[str, int]
    max_time_step: int
    time_steps: tuple[int, ...]
    even_time_steps: tuple[int, ...]
    odd_time_steps: tuple[int, ...]
    time_steps_4n_plus_1: tuple[int, ...]
    time_steps_4n_plus_3: tuple[int, ...]
    capacity: int
    initial_far_side_items: frozenset[str]
    buffer_time: int


def compute_max_time_step(
    num_items: int,
    capacity: int,
    buffer_time: int,
) -> int:
    """Compute the maximum time step T^max.

    T^max = 4 * (ceil(|I| / C) + T^buffer) + 2

    Args:
      num_items: Number of items |I|.
      capacity: Maximum number of items per load C.
      buffer_time: Buffer T^buffer.

    Returns:
      Maximum time step.
    """
    if num_items < 0:
        raise ValueError(f"num_items must be non-negative, got {num_items}")
    if capacity < 1:
        raise ValueError(f"capacity must be at least 1, got {capacity}")
    if buffer_time < 0:
        raise ValueError(f"buffer_time must be non-negative, got {buffer_time}")

    return 4 * (math.ceil(num_items / capacity) + buffer_time) + 2


def build_time_steps(max_time_step: int) -> tuple[int, ...]:
    """Return the time step set T = {0, ..., T^max}."""
    return tuple(range(max_time_step + 1))


def build_even_time_steps(max_time_step: int) -> tuple[int, ...]:
    """Return the even step set T^even = {0, 2, 4, ..., T^max}."""
    return tuple(range(0, max_time_step + 1, 2))


def build_odd_time_steps(max_time_step: int) -> tuple[int, ...]:
    """Return the odd step set T^odd = {1, 3, ..., T^max - 1}."""
    return tuple(range(1, max_time_step, 2))


def build_time_steps_4n_plus_1(max_time_step: int) -> tuple[int, ...]:
    """Return the set of start-to-goal move steps T^{4n+1}."""
    return tuple(range(1, max_time_step, 4))


def build_time_steps_4n_plus_3(max_time_step: int) -> tuple[int, ...]:
    """Return the set of goal-to-start move steps T^{4n+3}."""
    return tuple(range(3, max_time_step - 2, 4))


def build_indices(spec: PuzzleSpec | BaseSpec) -> ProblemIndices:
    """Build indices and sets from a problem definition.

    Args:
      spec: Problem definition.

    Returns:
      Indices for the formulation.
    """
    max_time_step = compute_max_time_step(
        num_items=len(spec.items),
        capacity=spec.capacity,
        buffer_time=spec.buffer_time,
    )
    return ProblemIndices(
        items=spec.items,
        item_to_index={name: index for index, name in enumerate(spec.items)},
        max_time_step=max_time_step,
        time_steps=build_time_steps(max_time_step),
        even_time_steps=build_even_time_steps(max_time_step),
        odd_time_steps=build_odd_time_steps(max_time_step),
        time_steps_4n_plus_1=build_time_steps_4n_plus_1(max_time_step),
        time_steps_4n_plus_3=build_time_steps_4n_plus_3(max_time_step),
        capacity=spec.capacity,
        initial_far_side_items=spec.initial_far_side,
        buffer_time=spec.buffer_time,
    )
