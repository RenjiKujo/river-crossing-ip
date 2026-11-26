# river-crossing-ip

**Languages:** [English](README.md) | [日本語](README.ja.md)

## Overview

A demo-ready Python library that solves the *Dr. Stone* river-crossing puzzle with **mixed-integer linear programming (MILP)**.  
Aimed at readers interested in mathematical optimization, combinatorial optimization, and river-crossing puzzles.

🎬 **Explainer (YouTube Shorts):** [Solving the Dr. Stone river-crossing puzzle with integer programming](https://youtube.com/shorts/eGgKSlvQKQs)

| Keywords | |
|----------|---|
| Source work | Dr. Stone |
| Methods | Integer programming / mathematical optimization / Pyomo / HiGHS |
| Puzzle types | Classic (wolf–goat–cabbage), Dr. Stone variant |

---

A Python library that solves river-crossing puzzles with **integer programming (IP)**.  
Models are built with [Pyomo](https://pyomo.readthedocs.io/) and solved with [HiGHS](https://highs.dev/).

The classic wolf–goat–cabbage puzzle and the Dr. Stone variant share the same model skeleton.

## Requirements

- Python 3.10+
- Dependencies: `pyomo`, `highspy`, `PyYAML` (installed via `pip install -e .`)

## Installation

### As a library

```bash
pip install "git+https://github.com/RenjiKujo/river-crossing-ip.git"
```

### For development (clone and contribute)

```bash
git clone https://github.com/RenjiKujo/river-crossing-ip.git
cd river-crossing-ip
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e ".[dev]"
```

## Quick start

Solve the classic puzzle (wolf, goat, and cabbage):

```bash
.venv/bin/python runner/solve.py --spec examples/classic.yaml
```

Dr. Stone variant:

```bash
.venv/bin/python runner/solve.py --spec examples/dr_stone.yaml
```

Solve and export a vertical YouTube Shorts mp4 (1080x1920) in one shot (`classic` / `dr_stone`). Extra deps (`matplotlib`, `imageio-ffmpeg`) are required; `imageio-ffmpeg` ships an ffmpeg binary:

```bash
pip install -e ".[animate]"
.venv/bin/python runner/animate.py --spec examples/classic.yaml --output out/classic_short.mp4
.venv/bin/python runner/animate.py --spec examples/dr_stone.yaml --output out/dr_stone_short.mp4
```

If `--output` is omitted, the path is `out/{puzzle_type}_short.mp4`. Use `--no-intro` to skip the title card, or `--intro-seconds 1.0` to change its duration.

List registered puzzle types:

```bash
.venv/bin/python runner/solve.py --list-types
```

Add `--tee` to show solver logs (`solve.py` / `animate.py`).

## Python API

```python
from river_crossing_ip import Engine

result = Engine().run("examples/classic.yaml")
print(result.status)          # "optimal"
print(result.finish_step)     # first step when everyone is on the goal side
print(result.objective_value) # objective value (min steps, plus extras for some types)
```

You can also call `load_spec` for YAML loading and `build_model` / `solve_model` separately.

## Puzzle types

| `puzzle_type` | Summary | Sample |
|---------------|---------|--------|
| `classic` | Capacity, pilots, grudge rules (a guardian is required when a forbidden pair shares a location) | [examples/classic.yaml](examples/classic.yaml) |
| `dr_stone` | Weight limits, suspicious members, craft/battle roles, etc. | [examples/dr_stone.yaml](examples/dr_stone.yaml) |

Problem definitions are written in YAML. Start from the samples above when adding a new instance.

## Pipeline

```text
YAML (examples/*.yaml)
  → load_spec()     load and validate the problem definition
  → build_model()   build the Pyomo model (shared + type-specific constraints)
  → solve_model()   solve with HiGHS
  → SolveResult     per-step placement and objective value
```

## Project layout

```text
src/river_crossing_ip/
  engine.py                 # load-to-solve pipeline
  types.py                  # PuzzleSpec, ClassicSpec, DrStoneSpec
  load_data/spec_loader.py  # YAML loading
  build_model/
    builder.py              # model construction
    indices.py              # indices and horizon
    constraints/            # shared, classic, and dr_stone constraints / objectives
  solve/
    solver.py               # HiGHS solve
    result.py               # SolveResult
runner/
  solve.py                  # CLI
  display.py                # result printing
  animate.py                # solve-result animation mp4 (classic / dr_stone)
  animation/                # drawing and export
examples/                   # sample problem definitions
docs/                       # problem rules and formulation notes
tests/                      # integration tests
```

## Documentation

| File | Content |
|------|---------|
| [docs/README.md](docs/README.md) | Problem setup |
| [docs/formulation/common.md](docs/formulation/common.md) | Shared IP formulation |
| [docs/formulation/classic.md](docs/formulation/classic.md) | classic extras |
| [docs/formulation/dr_stone.md](docs/formulation/dr_stone.md) | dr_stone extras |

Japanese translations: [README.ja.md](README.ja.md), [docs/README.ja.md](docs/README.ja.md), and `docs/formulation/*.ja.md`.

## Tests

```bash
pytest -q
```

Confirms that `examples/classic.yaml` and `examples/dr_stone.yaml` reach optimal solutions.

PRs and pushes to `main` run lint (ruff) and tests (pytest) via GitHub Actions (`.github/workflows/ci.yml`).

## License

MIT ([LICENSE](LICENSE))
