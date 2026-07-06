# river-crossing-ip

## 概要

『ドクターストーン』の川渡りパズルを **整数計画法（MILP）** で解くデモ付き Python ライブラリです。  
数理最適化・組合せ最適化・川渡りパズルに興味がある方向け。

| キーワード | |
|-----------|---|
| 対象作品 | ドクターストーン（Dr. Stone） |
| 手法 | 整数計画法 / 数理最適化 / Pyomo / HiGHS |
| 対応問題 | 古典（狼・羊・キャベツ）、ドクターストーン版 |

---

川渡りパズルを **整数計画（IP）** で解く Python ライブラリです。  
[Pyomo](https://pyomo.readthedocs.io/) でモデルを組み立て、[HiGHS](https://highs.dev/) で求解します。

古典問題（狼羊キャベツ）とドクターストーン版を、同じ骨格で扱えます。

## 要件

- Python 3.10 以上
- 依存: `pyomo`, `highspy`, `PyYAML`（`pip install -e .` で導入）

## インストール

### 使う場合（ライブラリとして組み込む）

```bash
pip install "git+https://github.com/RenjiKujo/river-crossing-ip.git"
```

### 開発する場合（clone して拡張・PR）

```bash
git clone https://github.com/RenjiKujo/river-crossing-ip.git
cd river-crossing-ip
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e ".[dev]"
```

## クイックスタート

古典問題（狼と羊とキャベツ）を解く:

```bash
.venv/bin/python runner/solve.py --spec examples/classic.yaml
```

ドクターストーン版:

```bash
.venv/bin/python runner/solve.py --spec examples/dr_stone.yaml
```

求解から YouTube Shorts 向け縦型 mp4（1080x1920）まで一括で行う場合（`dr_stone` のみ）。追加依存（`matplotlib`, `imageio-ffmpeg`）が必要です。`imageio-ffmpeg` に ffmpeg バイナリが同梱されます:

```bash
pip install -e ".[animate]"
.venv/bin/python runner/animate.py --spec examples/dr_stone.yaml --output out/dr_stone_short.mp4
```

`--no-intro` で冒頭タイトルカードを省略、`--intro-seconds 1.0` で表示秒数を変更できます。

登録済みの問題タイプを確認:

```bash
.venv/bin/python runner/solve.py --list-types
```

ソルバーログを表示する場合は `--tee` を付けます（`solve.py` / `animate.py` 共通）。

## Python API

```python
from river_crossing_ip import Engine

result = Engine().run("examples/classic.yaml")
print(result.status)          # "optimal"
print(result.finish_step)     # 全員が到達側にいる最初のステップ
print(result.objective_value) # 目的関数値（最小ステップ数）
```

`load_spec` で YAML を読み込み、`build_model` / `solve_model` を個別に呼ぶこともできます。

## 問題タイプ

| `puzzle_type` | 概要 | サンプル |
|---------------|------|----------|
| `classic` | 人数上限・操縦者・遺恨ルール（同地点に特定の組がいるとき仲裁者が必要） | [examples/classic.yaml](examples/classic.yaml) |
| `dr_stone` | 重量制限・疑いありメンバー・クラフト/バトル役割など | [examples/dr_stone.yaml](examples/dr_stone.yaml) |

問題定義は YAML で記述します。新しい問題を作るときは上記サンプルをベースにしてください。

## 処理の流れ

```text
YAML (examples/*.yaml)
  → load_spec()     問題定義の読み込み・検証
  → build_model()   Pyomo モデル構築（共通制約 + タイプ別制約）
  → solve_model()   HiGHS による求解
  → SolveResult     ステップごとの配置・目的関数値
```

## プロジェクト構成

```text
src/river_crossing_ip/
  engine.py                 # 読込〜求解のパイプライン
  types.py                  # PuzzleSpec, ClassicSpec, DrStoneSpec
  load_data/spec_loader.py  # YAML 読み込み
  build_model/
    builder.py              # モデル構築
    indices.py              # インデックス・ホライゾン計算
    constraints/            # 共通・classic・dr_stone の制約と目的関数
  solve/
    solver.py               # HiGHS 求解
    result.py               # SolveResult
runner/
  solve.py                  # CLI
  display.py                # 結果の表示
  animate.py                # 求解結果アニメ mp4 生成（dr_stone）
  animation/                # アニメ描画・書き出し
examples/                   # 問題定義サンプル
docs/                       # 問題設定・定式化メモ
tests/                      # 統合テスト
```

## ドキュメント

| ファイル | 内容 |
|----------|------|
| [docs/README.md](docs/README.md) | 問題設定の説明 |
| [docs/formulation/common.md](docs/formulation/common.md) | 共通 IP 定式化 |
| [docs/formulation/classic.md](docs/formulation/classic.md) | classic 向け追加ルール |
| [docs/formulation/dr_stone.md](docs/formulation/dr_stone.md) | dr_stone 向け追加ルール |

## テスト

```bash
pytest -q
```

`examples/classic.yaml` と `examples/dr_stone.yaml` が最適解に到達することを確認します。

PR と `main` への push では、lint（ruff）・テスト（pytest）を GitHub Actions で検証しています（`.github/workflows/ci.yml`）。

## ライセンス

MIT（[LICENSE](LICENSE)）
