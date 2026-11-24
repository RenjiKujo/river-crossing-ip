"""classic 向けアニメーション統合テスト。"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

RUNNER_DIR = Path(__file__).resolve().parents[1] / "runner"
sys.path.insert(0, str(RUNNER_DIR))

HAS_ANIMATE = importlib.util.find_spec("matplotlib") is not None

from river_crossing_ip.engine import Engine  # noqa: E402
from river_crossing_ip.load_data import load_spec  # noqa: E402
from river_crossing_ip.types import ClassicSpec  # noqa: E402

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"
CLASSIC_YAML = EXAMPLES_DIR / "classic.yaml"


@unittest.skipUnless(HAS_ANIMATE, "animate extras not installed")
class ClassicAnimationExportTest(unittest.TestCase):
    """classic.yaml の mp4 書き出し統合テスト。"""

    def test_classic_example_exports_mp4(self) -> None:
        spec = load_spec(CLASSIC_YAML)
        assert isinstance(spec, ClassicSpec)
        result = Engine().run_from_spec(spec)
        self.assertEqual(result.status, "optimal")
        self.assertIsNotNone(result.finish_step)

        from animation.draw import create_canvas
        from animation.export import export_mp4

        figure, axes = create_canvas()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                output_path = Path(tmp) / "classic_short.mp4"
                export_mp4(
                    figure,
                    axes,
                    result,
                    spec,
                    output_path,
                    intro_seconds=0.1,
                    include_intro=False,
                )
                self.assertTrue(output_path.is_file())
                self.assertGreater(output_path.stat().st_size, 0)
        finally:
            import matplotlib.pyplot as plt

            plt.close(figure)


if __name__ == "__main__":
    unittest.main()
