"""Frame drawing with matplotlib."""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch

from animation.layout import (
    CardStyle,
    StepLayout,
    build_step_layout,
    card_style_for_item,
    display_name,
)
from animation.phases import phase_label, ropeway_state
from river_crossing_ip.types import ClassicSpec, DrStoneSpec, PuzzleSpec

if TYPE_CHECKING:
    from river_crossing_ip.solve.result import SolveResult

# YouTube Shorts vertical format
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920
CANVAS_DPI = 100

# Layout regions (y coordinates, from the top)
HEADER_BOTTOM = 170
NEAR_BOTTOM = 760
ROPEWAY_BOTTOM = 1160
# FAR spans 1160 to 1920

CARD_GAP = 12
HIGHLIGHT_COLOR = "#FFF59D"
HIGHLIGHT_EDGE_COLOR = "#F9A825"
SUSP_COLOR = "#C62828"
BATTLE_COLOR = "#212121"
TRUSTED_BATTLE_COLOR = "#1565C0"
PILOT_COLOR = "#2E7D32"
BG_COLOR = "#F5F5F5"
ROPEWAY_BG = "#E3F2FD"
DEFAULT_EDGE_COLOR = "#424242"


def create_canvas() -> tuple[Figure, Axes]:
    """Create a 1080x1920 drawing canvas."""
    fig_w = CANVAS_WIDTH / CANVAS_DPI
    fig_h = CANVAS_HEIGHT / CANVAS_DPI
    figure = plt.figure(figsize=(fig_w, fig_h), dpi=CANVAS_DPI)
    axes = figure.add_axes([0, 0, 1, 1])
    axes.set_xlim(0, CANVAS_WIDTH)
    axes.set_ylim(CANVAS_HEIGHT, 0)
    axes.axis("off")
    figure.patch.set_facecolor(BG_COLOR)
    return figure, axes


def _grid_cols(count: int) -> int:
    """Return the number of columns by item count (fewer items give larger cards)."""
    if count <= 2:
        return max(1, count)
    if count <= 6:
        return 2
    return 3


def _grid_metrics(
    count: int, area_top: float, area_bottom: float
) -> tuple[float, float, float, float, int]:
    """Return the card width, height, origin, and column count of the in-area grid."""
    area_height = area_bottom - area_top
    area_width = CANVAS_WIDTH - 40
    margin_x = 20.0
    cols = _grid_cols(count)

    rows = max(1, (count + cols - 1) // cols)
    card_w = (area_width - CARD_GAP * (cols - 1)) / cols
    card_h = min(130.0, (area_height - CARD_GAP * (rows - 1)) / rows)
    card_h = max(78.0, card_h)
    return card_w, card_h, margin_x, area_top, cols


def _draw_badge(
    axes: Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    label: str,
    *,
    facecolor: str,
    text_color: str = "white",
) -> None:
    """Draw the badge for the top-right of a card."""
    badge = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.01,rounding_size=3",
        linewidth=0,
        facecolor=facecolor,
    )
    axes.add_patch(badge)
    axes.text(
        x + width / 2,
        y + height / 2,
        label,
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
        color=text_color,
    )


def _draw_card(
    axes: Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    item: str,
    *,
    card_style: CardStyle,
    highlighted: bool,
    name_fontsize: float,
    weight_kg: int | None = None,
    weight_fontsize: float = 11.0,
) -> None:
    """Draw a single member card."""
    facecolor = HIGHLIGHT_COLOR if highlighted else "white"
    if card_style == CardStyle.PILOT:
        edgecolor = PILOT_COLOR
        linestyle = "solid"
        linewidth = 2.5
    elif card_style == CardStyle.TRUSTED_BATTLE:
        edgecolor = TRUSTED_BATTLE_COLOR
        linestyle = "solid"
        linewidth = 2.5
    elif card_style == CardStyle.SUSP_BATTLE:
        edgecolor = SUSP_COLOR
        linestyle = "solid"
        linewidth = 2.5
    elif card_style == CardStyle.SUSP_ONLY:
        edgecolor = SUSP_COLOR
        linestyle = (0, (4, 3))
        linewidth = 2.5
    else:
        edgecolor = DEFAULT_EDGE_COLOR
        linestyle = "solid"
        linewidth = 1.8

    if highlighted:
        # Keep the frame color (attribute) and emphasize only the thickness
        linewidth = max(linewidth, 3.5)
        if card_style == CardStyle.DEFAULT:
            edgecolor = HIGHLIGHT_EDGE_COLOR

    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=8",
        linewidth=linewidth,
        edgecolor=edgecolor,
        facecolor=facecolor,
        linestyle=linestyle,
    )
    axes.add_patch(patch)

    draw_name_fs = name_fontsize + 2.0 if highlighted else name_fontsize
    if weight_kg is None:
        name_y = y + height * 0.55
    else:
        name_y = y + height * 0.38
        weight_y = y + height * 0.72
        draw_weight_fs = weight_fontsize + 1.5 if highlighted else weight_fontsize
        axes.text(
            x + width / 2,
            weight_y,
            f"{weight_kg} kg",
            ha="center",
            va="center",
            fontsize=draw_weight_fs,
            fontweight="bold" if highlighted else "normal",
            color="#424242",
        )

    axes.text(
        x + width / 2,
        name_y,
        display_name(item),
        ha="center",
        va="center",
        fontsize=draw_name_fs,
        fontweight="bold",
        color="#212121",
    )

    badge_h = 18.0
    badge_w = min(52.0, width * 0.40)
    badge_y = y + 5
    badge_gap = 3.0
    right_x = x + width - badge_w - 5

    if card_style == CardStyle.PILOT:
        _draw_badge(
            axes,
            right_x,
            badge_y,
            badge_w,
            badge_h,
            "PILOT",
            facecolor=PILOT_COLOR,
        )
    elif card_style == CardStyle.SUSP_BATTLE:
        battle_x = right_x
        susp_x = battle_x - badge_w - badge_gap
        _draw_badge(
            axes,
            susp_x,
            badge_y,
            badge_w,
            badge_h,
            "SUSP",
            facecolor=SUSP_COLOR,
        )
        _draw_badge(
            axes,
            battle_x,
            badge_y,
            badge_w,
            badge_h,
            "BATTLE",
            facecolor=BATTLE_COLOR,
        )
    elif card_style == CardStyle.SUSP_ONLY:
        _draw_badge(
            axes,
            right_x,
            badge_y,
            badge_w,
            badge_h,
            "SUSP",
            facecolor=SUSP_COLOR,
        )
    elif card_style == CardStyle.TRUSTED_BATTLE:
        _draw_badge(
            axes,
            right_x,
            badge_y,
            badge_w,
            badge_h,
            "BATTLE",
            facecolor=BATTLE_COLOR,
        )


def _draw_item_grid(
    axes: Axes,
    items: tuple[str, ...],
    area_top: float,
    area_bottom: float,
    spec: PuzzleSpec,
    moved_items: frozenset[str],
) -> None:
    """Draw a card grid inside an area."""
    if not items:
        return

    card_w, card_h, margin_x, origin_y, cols = _grid_metrics(
        len(items),
        area_top,
        area_bottom,
    )
    show_weight = isinstance(spec, DrStoneSpec)
    if show_weight:
        name_fs = max(13.0, min(20.0, card_w * 0.17))
        weight_fs = max(11.0, min(16.0, card_w * 0.13))
    else:
        name_fs = max(16.0, min(28.0, card_w * 0.22))
        weight_fs = 11.0

    for index, item in enumerate(items):
        col = index % cols
        row = index // cols
        x = margin_x + col * (card_w + CARD_GAP)
        y = origin_y + row * (card_h + CARD_GAP)
        weight_kg: int | None = None
        if show_weight:
            weight_kg = int(spec.item_weights[item])
        _draw_card(
            axes,
            x,
            y,
            card_w,
            card_h,
            item,
            card_style=card_style_for_item(item, spec),
            highlighted=item in moved_items,
            name_fontsize=name_fs,
            weight_kg=weight_kg,
            weight_fontsize=weight_fs,
        )


def _draw_section_label(axes: Axes, label: str, y: float) -> None:
    """Draw an area heading."""
    axes.text(
        CANVAS_WIDTH / 2,
        y,
        label,
        ha="center",
        va="center",
        fontsize=22,
        fontweight="bold",
        color="#37474F",
    )


def _draw_header(
    axes: Axes,
    step: int,
    finish_step: int,
    layout: StepLayout,
    max_load_kg: int | None,
) -> None:
    """Draw the header (Step / Phase / Load)."""
    phase = phase_label(step, len(layout.transit_items))
    axes.text(
        40,
        48,
        f"Step {step} / {finish_step}",
        ha="left",
        va="center",
        fontsize=26,
        fontweight="bold",
        color="#212121",
    )
    axes.text(
        CANVAS_WIDTH / 2,
        105,
        phase,
        ha="center",
        va="center",
        fontsize=28,
        fontweight="bold",
        color="#1565C0",
    )
    if layout.load_kg is not None and max_load_kg is not None:
        axes.text(
            CANVAS_WIDTH - 40,
            48,
            f"Load {layout.load_kg} / {max_load_kg} kg",
            ha="right",
            va="center",
            fontsize=20,
            fontweight="bold",
            color="#424242",
        )


def _vehicle_label(
    layout: StepLayout,
    *,
    vehicle_name: str,
    dock_label: str | None,
    is_empty: bool,
    has_motion: bool,
) -> str:
    """Build the vehicle label for the center band."""
    if layout.load_kg is not None:
        return f"[{vehicle_name} {layout.load_kg} kg]"
    if is_empty and has_motion:
        return f"[{vehicle_name} empty]"
    if dock_label is not None:
        return f"[{vehicle_name} docked @ {dock_label}]"
    return f"[{vehicle_name}]"


def _draw_vehicle_band(
    axes: Axes,
    step: int,
    layout: StepLayout,
    spec: PuzzleSpec,
    moved_items: frozenset[str],
) -> None:
    """Draw the vehicle band (BOAT / GONDOLA)."""
    top = NEAR_BOTTOM + 10
    bottom = ROPEWAY_BOTTOM - 10
    band = FancyBboxPatch(
        (20, top),
        CANVAS_WIDTH - 40,
        bottom - top,
        boxstyle="round,pad=0.01,rounding_size=8",
        linewidth=1.0,
        edgecolor="#90CAF9",
        facecolor=ROPEWAY_BG,
    )
    axes.add_patch(band)

    cable_y = (top + bottom) / 2
    axes.plot([60, CANVAS_WIDTH - 60], [cable_y, cable_y], color="#546E7A", linewidth=3)

    state = ropeway_state(step, layout.transit_items)
    if state.motion_symbol:
        axes.text(
            80,
            cable_y - 28,
            state.motion_symbol,
            ha="left",
            va="center",
            fontsize=28,
            fontweight="bold",
            color="#1565C0",
        )
        axes.text(
            CANVAS_WIDTH - 80,
            cable_y - 28,
            state.motion_symbol,
            ha="right",
            va="center",
            fontsize=28,
            fontweight="bold",
            color="#1565C0",
        )

    vehicle_name = "BOAT" if isinstance(spec, ClassicSpec) else "GONDOLA"
    label = _vehicle_label(
        layout,
        vehicle_name=vehicle_name,
        dock_label=state.dock_label,
        is_empty=state.is_empty,
        has_motion=bool(state.motion_symbol),
    )
    axes.text(
        CANVAS_WIDTH / 2,
        cable_y - 30,
        label,
        ha="center",
        va="center",
        fontsize=18,
        fontweight="bold",
        color="#37474F",
    )

    if layout.transit_items:
        transit_top = cable_y + 20
        transit_bottom = bottom - 20
        _draw_item_grid(
            axes,
            layout.transit_items,
            transit_top,
            transit_bottom,
            spec,
            moved_items,
        )


def draw_step_frame(
    axes: Axes,
    step: int,
    result: SolveResult,
    spec: PuzzleSpec,
) -> None:
    """Draw the frame for one step (clear axes and redraw)."""
    axes.clear()
    axes.set_xlim(0, CANVAS_WIDTH)
    axes.set_ylim(CANVAS_HEIGHT, 0)
    axes.axis("off")

    assert result.finish_step is not None
    layout = build_step_layout(step, result.positions, spec)

    max_load_kg: int | None = None
    if isinstance(spec, DrStoneSpec):
        max_load_kg = int(spec.max_load_weight)

    _draw_header(axes, step, result.finish_step, layout, max_load_kg)
    _draw_section_label(axes, "NEAR SIDE", NEAR_BOTTOM - 24)
    _draw_item_grid(
        axes,
        layout.near_items,
        HEADER_BOTTOM,
        NEAR_BOTTOM - 36,
        spec,
        layout.moved_items,
    )
    _draw_vehicle_band(axes, step, layout, spec, layout.moved_items)
    _draw_section_label(axes, "FAR SIDE", ROPEWAY_BOTTOM + 14)
    _draw_item_grid(
        axes,
        layout.far_items,
        ROPEWAY_BOTTOM + 36,
        CANVAS_HEIGHT - 20,
        spec,
        layout.moved_items,
    )


def draw_intro_frame(
    axes: Axes,
    finish_step: int,
    *,
    puzzle_type: str = "dr_stone",
) -> None:
    """Draw the intro frame."""
    axes.clear()
    axes.set_xlim(0, CANVAS_WIDTH)
    axes.set_ylim(CANVAS_HEIGHT, 0)
    axes.axis("off")
    axes.set_facecolor(BG_COLOR)

    if puzzle_type == "classic":
        title = "Classic River Crossing"
    else:
        title = "Dr. Stone River Crossing"

    lines = [
        title,
        "IP Optimal Solution",
        f"{finish_step} steps",
    ]
    y_start = CANVAS_HEIGHT / 2 - 90
    for index, line in enumerate(lines):
        fontsize = 40 if index == 0 else 28
        axes.text(
            CANVAS_WIDTH / 2,
            y_start + index * 80,
            line,
            ha="center",
            va="center",
            fontsize=fontsize,
            fontweight="bold",
            color="#212121",
        )
