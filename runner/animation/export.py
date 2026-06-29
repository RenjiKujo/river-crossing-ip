"""フレーム列の mp4 書き出し。"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from matplotlib.animation import FFMpegWriter
from matplotlib.figure import Figure

from animation.draw import CANVAS_DPI, draw_intro_frame, draw_step_frame
from animation.layout import step_duration

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from river_crossing_ip.solve.result import SolveResult
    from river_crossing_ip.types import DrStoneSpec

FFMPEG_INSTALL_HINT = (
    "ffmpeg is required for mp4 export. "
    'Install animate extras (pip install -e ".[animate]") '
    "or system ffmpeg: sudo apt install ffmpeg"
)


def _configure_ffmpeg() -> None:
    """利用可能な ffmpeg 実行ファイルを matplotlib に設定する。"""
    import matplotlib as mpl

    try:
        import imageio_ffmpeg

        mpl.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
        return
    except ImportError:
        pass

    import shutil

    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg is not None:
        mpl.rcParams["animation.ffmpeg_path"] = system_ffmpeg


def export_mp4(
    figure: Figure,
    axes: Axes,
    result: SolveResult,
    spec: DrStoneSpec,
    output_path: Path,
    *,
    fps: int = 30,
    intro_seconds: float = 2.0,
    include_intro: bool = True,
) -> None:
    """求解結果アニメーションを mp4 に書き出す。

    Args:
      figure: matplotlib Figure。
      axes: 描画 Axes。
      result: 求解結果。
      spec: dr_stone 問題定義。
      output_path: 出力 mp4 パス。
      fps: フレームレート。
      intro_seconds: イントロ表示秒数。
      include_intro: イントロフレームを含めるか。

    Raises:
      RuntimeError: ffmpeg 未インストール等で書き出し失敗時。
    """
    if result.finish_step is None or result.status != "optimal":
        raise ValueError("optimal result with finish_step is required")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    _configure_ffmpeg()

    try:
        writer = FFMpegWriter(fps=fps)
    except Exception as exc:
        raise RuntimeError(FFMPEG_INSTALL_HINT) from exc

    try:
        with writer.saving(figure, str(output_path), dpi=CANVAS_DPI):
            if include_intro:
                draw_intro_frame(axes, result.finish_step)
                _grab_for_seconds(writer, figure, intro_seconds, fps)

            for step in range(result.finish_step + 1):
                draw_step_frame(axes, step, result, spec)
                duration = step_duration(step, result.positions)
                _grab_for_seconds(writer, figure, duration, fps)
    except (FileNotFoundError, OSError) as exc:
        raise RuntimeError(FFMPEG_INSTALL_HINT) from exc


def _grab_for_seconds(
    writer: FFMpegWriter,
    figure: Figure,
    seconds: float,
    fps: int,
) -> None:
    """指定秒数分 grab_frame する。"""
    frame_count = max(1, int(seconds * fps))
    for _ in range(frame_count):
        writer.grab_frame()
