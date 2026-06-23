# 川渡りパズル定式化（共通項）

`puzzle_type` に依存しない整数計画モデルの骨格。ルールの説明は [../README.md](../README.md#問題設定) を参照。

## インデックス

| 記号 | 定義域 | 説明 | 単位 | 参照 |
|------|--------|------|------|------|
| $i$ | $\mathcal{I}$ | 対象のインデックス | — | `item` |
| $t$ | $\mathcal{T}$ | 時間ステップ | ステップ | `time_step` |

## パラメータ

| 記号 | 定義域 | 説明 | 参照 |
|------|--------|------|------|
| $T^{\text{max}}$ | $\mathbb{N}$ | 最大時間ステップ | `MAX_TIME_STEP` |
| $T^{\text{buffer}}$ | $\mathbb{N}_0$ | タイムステップに対するバッファー | `BUFFER_TIME` |
| $C$ | $\mathbb{N}$ | 最大積載人数 | `MAX_CAPACITY` |

$T^{\text{max}}$ は次の式で与える。

$$
T^{\text{max}} = 4 \left( \left\lceil \frac{|\mathcal{I}|}{C} \right\rceil + T^{\text{buffer}} \right) + 2
$$


## 集合

| 記号 | 全要素 | 説明 | 参照 |
|------|------|------|------|
| $\mathcal{I}$ | 問題による | 移動対象の集合 | `items` |
| $\mathcal{I}_0^{\text{goal}}$ | $\mathcal{I}_0^{\text{goal}} \subseteq \mathcal{I}$（問題による） | ステップ0から到達側にいる対象の集合 | `initial_far_side_items` |
| $\mathcal{T}$ | $\{0, 1, \ldots, T^{\text{max}}\}$ | 時間ステップの集合 | `time_steps` |
| $\mathcal{T}^{\text{even}}$ | $\{0, 2, 4, \ldots, T^{\text{max}}\}$ | 偶数ステップ（ステップ0は初期配置、それ以降は乗り降り） | `even_time_steps` |
| $\mathcal{T}^{\text{odd}}$ | $\{1, 3, 5, \ldots, (T^{\text{max}}-1)\}$ | 奇数ステップ（移動） | `odd_time_steps` |
| $\mathcal{T}^{4n+1}$ | $\{1, 5, 9, \ldots, (T^{\text{max}}-1)\}$ | 4で割ったとき、余りが1のステップ（出発側から到達側への移動） | `time_steps_4n_plus_1` |
| $\mathcal{T}^{4n+3}$ | $\{3, 7, 11, \ldots, (T^{\text{max}}-3)\}$ | 4で割ったとき、余りが3のステップ（到達側から出発側への移動） | `time_steps_4n_plus_3` |


## 決定変数

| 変数 | 定義域 | 意味 | 参照 |
|------|--------|------|------|
| $\delta_{i,t}^{\text{start}}$ | $\{0, 1\}$ | ステップ $t$ において対象 $i$ が出発側にいるとき 1 | `delta_start` |
| $\delta_{i,t}^{\text{goal}}$ | $\{0, 1\}$ | ステップ $t$ において対象 $i$ が到達側にいるとき 1 | `delta_goal` |
| $\delta_{i,t}^{\text{transit}}$ | $\{0, 1\}$ | ステップ $t$ において対象 $i$ が移動中のとき 1 | `delta_transit` |
| $f_t$ | $\{0, 1\}$ | ステップ $t$ において、すべての対象が到達側にいるとき 1 | `finish_flag` |

目的関数は `puzzle_type` ごとに [classic.md](classic.md) または [dr_stone.md](dr_stone.md) を参照。

## 制約

`puzzle_type` が `classic` でも `dr_stone` でも同じ制約は以下の通り。

### 位置の一意性

すべての対象は、各タイムステップにおいて、どこか1箇所に存在する:

$$
\delta_{i,t}^{\text{start}} + \delta_{i,t}^{\text{goal}} + \delta_{i,t}^{\text{transit}} = 1
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T})
\tag{C1-1}
$$

### 状態遷移

偶数ステップではすべての対象は移動中ではない:

$$
\delta_{i,t}^{\text{transit}} = 0
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{\text{even}})
\tag{C2-1}
$$

$t \in \mathcal{T}^{4n+1}$（出発側→到達側の移動）では、対象 $i$ がステップ $t$ で移動中であることと、直前のステップ $t-1$ で出発側にいること・直後のステップ $t+1$ で到達側にいることは必要十分である:

$$
\delta_{i,t}^{\text{transit}} = 1
\quad \Leftrightarrow \quad
\delta_{i,t-1}^{\text{start}} = 1 \;\wedge\; \delta_{i,t+1}^{\text{goal}} = 1
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{4n+1})
$$

線形計画では次のように記述する:

$$
\delta_{i,t}^{\text{transit}} \leq \delta_{i,t-1}^{\text{start}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{4n+1})
\tag{C2-2}
$$

$$
\delta_{i,t}^{\text{transit}} \leq \delta_{i,t+1}^{\text{goal}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{4n+1})
\tag{C2-3}
$$

$$
\delta_{i,t}^{\text{transit}} \geq \delta_{i,t-1}^{\text{start}} + \delta_{i,t+1}^{\text{goal}} - 1
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{4n+1})
\tag{C2-4}
$$

$t \in \mathcal{T}^{4n+3}$（到達側→出発側の移動）では、対象 $i$ がステップ $t$ で移動中であることと、直前のステップ $t-1$ で到達側にいること・直後のステップ $t+1$ で出発側にいることは必要十分である:

$$
\delta_{i,t}^{\text{transit}} = 1
\quad \Leftrightarrow \quad
\delta_{i,t-1}^{\text{goal}} = 1 \;\wedge\; \delta_{i,t+1}^{\text{start}} = 1
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{4n+3})
$$

線形計画では次のように記述する:

$$
\delta_{i,t}^{\text{transit}} \leq \delta_{i,t-1}^{\text{goal}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{4n+3})
\tag{C2-5}
$$

$$
\delta_{i,t}^{\text{transit}} \leq \delta_{i,t+1}^{\text{start}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{4n+3})
\tag{C2-6}
$$

$$
\delta_{i,t}^{\text{transit}} \geq \delta_{i,t-1}^{\text{goal}} + \delta_{i,t+1}^{\text{start}} - 1
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{4n+3})
\tag{C2-7}
$$

移動ステップ $t \in \mathcal{T}^{\text{odd}}$ において、対象 $i$ が移動中でないとき、出発側・到達側の位置はそれぞれ直前・現在・直後のステップ $t-1, t, t+1$ で変わらない:

$$
\delta_{i,t}^{\text{transit}} = 0
\quad \Rightarrow \quad
\delta_{i,t-1}^{\text{start}} = \delta_{i,t}^{\text{start}} = \delta_{i,t+1}^{\text{start}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{\text{odd}})
$$

$$
\delta_{i,t}^{\text{transit}} = 0
\quad \Rightarrow \quad
\delta_{i,t-1}^{\text{goal}} = \delta_{i,t}^{\text{goal}} = \delta_{i,t+1}^{\text{goal}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{\text{odd}})
$$

線形計画では次のように記述する:

$$
\delta_{i,t-1}^{\text{start}} - \delta_{i,t}^{\text{start}}
\leq \delta_{i,t}^{\text{transit}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{\text{odd}})
\tag{C2-8}
$$

$$
\delta_{i,t}^{\text{start}} - \delta_{i,t-1}^{\text{start}}
\leq \delta_{i,t}^{\text{transit}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{\text{odd}})
\tag{C2-9}
$$

$$
\delta_{i,t}^{\text{start}} - \delta_{i,t+1}^{\text{start}}
\leq \delta_{i,t}^{\text{transit}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{\text{odd}})
\tag{C2-10}
$$

$$
\delta_{i,t+1}^{\text{start}} - \delta_{i,t}^{\text{start}}
\leq \delta_{i,t}^{\text{transit}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{\text{odd}})
\tag{C2-11}
$$

$$
\delta_{i,t-1}^{\text{goal}} - \delta_{i,t}^{\text{goal}}
\leq \delta_{i,t}^{\text{transit}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{\text{odd}})
\tag{C2-12}
$$

$$
\delta_{i,t}^{\text{goal}} - \delta_{i,t-1}^{\text{goal}}
\leq \delta_{i,t}^{\text{transit}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{\text{odd}})
\tag{C2-13}
$$

$$
\delta_{i,t}^{\text{goal}} - \delta_{i,t+1}^{\text{goal}}
\leq \delta_{i,t}^{\text{transit}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{\text{odd}})
\tag{C2-14}
$$

$$
\delta_{i,t+1}^{\text{goal}} - \delta_{i,t}^{\text{goal}}
\leq \delta_{i,t}^{\text{transit}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{\text{odd}})
\tag{C2-15}
$$

### 初期状態

ステップ $t=0$ では、$\mathcal{I}_0^{\text{goal}}$ に含まれる対象だけが到達側にいる:

$$
\delta_{i,0}^{\text{goal}} = 1
\quad (\forall i \in \mathcal{I}_0^{\text{goal}})
\tag{C3-1}
$$

$$
\delta_{i,0}^{\text{goal}} = 0
\quad (\forall i \in \mathcal{I} \setminus \mathcal{I}_0^{\text{goal}})
\tag{C3-2}
$$

### フィニッシュフラグ

ステップ $t$ において、$\delta_{i,t}^{\text{goal}}$ の合計が対象数 $|\mathcal{I}|$ と一致するときかつそのときに限って、フィニッシュフラグ $f_t$ が 1 になる:

$$
\sum_{i \in \mathcal{I}} \delta_{i,t}^{\text{goal}} = |\mathcal{I}| \quad \Leftrightarrow \quad f_t = 1
$$

線形計画では次のように記述する:

$$
f_t \leq \delta_{i,t}^{\text{goal}}
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T})
\tag{C4-1}
$$

$$
f_t \geq 1 - |\mathcal{I}| + \sum_{i \in \mathcal{I}} \delta_{i,t}^{\text{goal}}
\quad (\forall t \in \mathcal{T})
\tag{C4-2}
$$

フィニッシュ後も到達側に留まる:

$$
f_t \leq f_{t+1}
\quad (\forall t \in \{0, 1, \ldots, (T^{\text{max}} - 1)\})
\tag{C4-3}
$$

ホライゾン内に必ず完了する:

$$
f_{T^{\text{max}}} = 1
\tag{C4-4}
$$

### 人数定員

$$
\sum_{i \in \mathcal{I}} \delta_{i,t}^{\text{transit}} \leq C
\quad (t \in \mathcal{T}^{\text{odd}})
\tag{C5-1}
$$

