"""dr_stone 向け Engine 統合テスト。"""

from __future__ import annotations

import unittest
from pathlib import Path

from river_crossing_ip.engine import Engine

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


class DrStoneEngineSolveTest(unittest.TestCase):
    """dr_stone.yaml の Engine.run 統合テスト。"""

    def test_dr_stone_example_is_optimal(self) -> None:
        result = Engine().run(EXAMPLES_DIR / "dr_stone.yaml")
        self.assertEqual(result.status, "optimal")
        self.assertIsNotNone(result.finish_step)
        self.assertIsNotNone(result.objective_value)

        assert result.finish_step is not None
        self.assertGreaterEqual(result.finish_step, 1)

        final_positions = result.positions[result.finish_step]
        self.assertTrue(
            all(place == "goal" for place in final_positions.values()),
        )


if __name__ == "__main__":
    unittest.main()
