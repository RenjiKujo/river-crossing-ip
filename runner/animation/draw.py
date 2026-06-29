"""matplotlib によるフレーム描画。"""

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

if TYPE_CHECKING:
    from river_crossing_ip.solve.result import SolveResult
    from river_crossing_ip.types import DrStoneSpec

# YouTube Shorts 縦型
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920
CANVAS_DPI = 100

# レイアウト領域（y 座標、上から）
HEADER_BOTTOM = 160
NEAR_BOTTOM = 780
ROPEWAY_BOTTOM = 1140
# FAR は 1140〜1920

CARD_COLS = 4
CARD_GAP = 8
HIGHLIGHT_COLOR = "#FFF9C4"
SUSP_COLOR = "#C62828"
BATTLE_COLOR = "#212121"
TRUSTED_BATTLE_COLOR = "#1565C0"
BG_COLOR = "#F5F5F5"
ROPEWAY_BG = "#E3F2FD"
DEFAULT_EDGE_COLOR = "#424242"


def create_canvas() -> tuple[Figure, Axes]:
    """1080x1920 の描画キャンバスを作成する。"""
    fig_w = CANVAS_WIDTH / CANVAS_DPI
    fig_h = CANVAS_HEIGHT / CANVAS_DPI
    figure = plt.figure(figsize=(fig_w, fig_h), dpi=CANVAS_DPI)
    axes = figure.add_axes([0, 0, 1, 1])
    axes.set_xlim(0, CANVAS_WIDTH)
    axes.set_ylim(CANVAS_HEIGHT, 0)
    axes.axis("off")
    figure.patch.set_facecolor(BG_COLOR)
    return figure, axes


def _grid_metrics(
    count: int, area_top: float, area_bottom: float
) -> tuple[float, float, float, float]:
    """エリア内グリッドのカード幅・高さ・原点を返す。"""
    area_height = area_bottom - area_top
    area_width = CANVAS_WIDTH - 40
    margin_x = 20.0

    rows = max(1, (count + CARD_COLS - 1) // CARD_COLS)
    card_w = (area_width - CARD_GAP * (CARD_COLS - 1)) / CARD_COLS
    card_h = min(88.0, (area_height - CARD_GAP * (rows - 1)) / rows)
    card_h = max(52.0, card_h)
    return card_w, card_h, margin_x, area_top


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
    """カード右上用バッジを描画する。"""
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
        fontsize=7,
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
    weight_kg: int,
    *,
    card_style: CardStyle,
    highlighted: bool,
    name_fontsize: float,
    weight_fontsize: float,
) -> None:
    """メンバーカード1枚を描画する。"""
    facecolor = HIGHLIGHT_COLOR if highlighted else "white"
    if card_style == CardStyle.TRUSTED_BATTLE:
        edgecolor = TRUSTED_BATTLE_COLOR
        linestyle = "solid"
        linewidth = 2.0
    elif card_style == CardStyle.SUSP_BATTLE:
        edgecolor = SUSP_COLOR
        linestyle = "solid"
        linewidth = 2.0
    elif card_style == CardStyle.SUSP_ONLY:
        edgecolor = SUSP_COLOR
        linestyle = (0, (4, 3))
        linewidth = 2.0
    else:
        edgecolor = DEFAULT_EDGE_COLOR
        linestyle = "solid"
        linewidth = 1.2

    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=6",
        linewidth=linewidth,
        edgecolor=edgecolor,
        facecolor=facecolor,
        linestyle=linestyle,
    )
    axes.add_patch(patch)

    name_y = y + height * 0.32
    weight_y = y + height * 0.72
    axes.text(
        x + width / 2,
        name_y,
        display_name(item),
        ha="center",
        va="center",
        fontsize=name_fontsize,
        fontweight="bold",
        color="#212121",
    )
    axes.text(
        x + width / 2,
        weight_y,
        f"{weight_kg} kg",
        ha="center",
        va="center",
        fontsize=weight_fontsize,
        color="#616161",
    )

    badge_h = 14.0
    badge_w = min(38.0, width * 0.42)
    badge_y = y + 4
    badge_gap = 2.0
    right_x = x + width - badge_w - 4

    if card_style == CardStyle.SUSP_BATTLE:
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
    spec: DrStoneSpec,
    moved_items: frozenset[str],
) -> None:
    """エリア内にカードグリッドを描画する。"""
    if not items:
        return

    card_w, card_h, margin_x, origin_y = _grid_metrics(
        len(items),
        area_top,
        area_bottom,
    )
    name_fs = max(8.0, min(11.0, card_w * 0.14))
    weight_fs = max(7.0, min(9.0, card_w * 0.11))

    for index, item in enumerate(items):
        col = index % CARD_COLS
        row = index // CARD_COLS
        x = margin_x + col * (card_w + CARD_GAP)
        y = origin_y + row * (card_h + CARD_GAP)
        _draw_card(
            axes,
            x,
            y,
            card_w,
            card_h,
            item,
            int(spec.item_weights[item]),
            card_style=card_style_for_item(item, spec),
            highlighted=item in moved_items,
            name_fontsize=name_fs,
            weight_fontsize=weight_fs,
        )


def _draw_section_label(axes: Axes, label: str, y: float) -> None:
    """エリア見出しを描画する。"""
    axes.text(
        CANVAS_WIDTH / 2,
        y,
        label,
        ha="center",
        va="center",
        fontsize=18,
        fontweight="bold",
        color="#37474F",
    )


def _draw_header(
    axes: Axes,
    step: int,
    finish_step: int,
    layout: StepLayout,
    max_load_kg: int,
) -> None:
    """ヘッダー（Step / Phase / Load）を描画する。"""
    phase = phase_label(step, len(layout.transit_items))
    axes.text(
        40,
        50,
        f"Step {step} / {finish_step}",
        ha="left",
        va="center",
        fontsize=22,
        fontweight="bold",
        color="#212121",
    )
    axes.text(
        CANVAS_WIDTH / 2,
        100,
        phase,
        ha="center",
        va="center",
        fontsize=20,
        fontweight="bold",
        color="#1565C0",
    )
    if layout.load_kg is not None:
        axes.text(
            CANVAS_WIDTH - 40,
            50,
            f"Load {layout.load_kg} / {max_load_kg} kg",
            ha="right",
            va="center",
            fontsize=16,
            color="#424242",
        )


def _draw_ropeway_band(
    axes: Axes,
    step: int,
    layout: StepLayout,
    spec: DrStoneSpec,
    moved_items: frozenset[str],
) -> None:
    """ロープウェー帯を描画する。"""
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

    gondola_label = "[GONDOLA]"
    if layout.load_kg is not None:
        gondola_label = f"[GONDOLA {layout.load_kg} kg]"
    elif state.is_empty and state.motion_symbol:
        gondola_label = "[GONDOLA empty]"
    elif state.dock_label is not None:
        gondola_label = f"[GONDOLA docked @ {state.dock_label}]"

    axes.text(
        CANVAS_WIDTH / 2,
        cable_y - 30,
        gondola_label,
        ha="center",
        va="center",
        fontsize=14,
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
    spec: DrStoneSpec,
) -> None:
    """1ステップ分のフレームを描画する（axes をクリアして再描画）。"""
    axes.clear()
    axes.set_xlim(0, CANVAS_WIDTH)
    axes.set_ylim(CANVAS_HEIGHT, 0)
    axes.axis("off")

    assert result.finish_step is not None
    layout = build_step_layout(step, result.positions, spec)

    _draw_header(axes, step, result.finish_step, layout, int(spec.max_load_weight))
    _draw_section_label(axes, "NEAR SIDE", NEAR_BOTTOM - 24)
    _draw_item_grid(
        axes,
        layout.near_items,
        HEADER_BOTTOM,
        NEAR_BOTTOM - 36,
        spec,
        layout.moved_items,
    )
    _draw_ropeway_band(axes, step, layout, spec, layout.moved_items)
    _draw_section_label(axes, "FAR SIDE", ROPEWAY_BOTTOM + 14)
    _draw_item_grid(
        axes,
        layout.far_items,
        ROPEWAY_BOTTOM + 36,
        CANVAS_HEIGHT - 20,
        spec,
        layout.moved_items,
    )


def draw_intro_frame(axes: Axes, finish_step: int) -> None:
    """イントロフレームを描画する。"""
    axes.clear()
    axes.set_xlim(0, CANVAS_WIDTH)
    axes.set_ylim(CANVAS_HEIGHT, 0)
    axes.axis("off")
    axes.set_facecolor(BG_COLOR)

    lines = [
        "Dr. Stone River Crossing",
        "IP Optimal Solution",
        f"{finish_step} steps",
    ]
    y_start = CANVAS_HEIGHT / 2 - 80
    for index, line in enumerate(lines):
        fontsize = 32 if index == 0 else 24
        axes.text(
            CANVAS_WIDTH / 2,
            y_start + index * 70,
            line,
            ha="center",
            va="center",
            fontsize=fontsize,
            fontweight="bold",
            color="#212121",
        )
