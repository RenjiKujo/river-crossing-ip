# 川渡りパズル定式化（classic）

`puzzle_type: classic` 向けの追加定式化。共通骨格は [common.md](common.md)、ルールの説明は [../README.md](../README.md#classic) を参照。

インデックス・決定変数は [common.md](common.md) に従う。以下は classic で追加するインデックス・パラメータ・集合・目的関数・制約を記す。

## インデックス

| 記号 | 定義域 | 説明 | 単位 | 参照 |
|------|--------|------|------|------|
| $k$ | $\mathcal{K}$ | 遺恨ルールのインデックス | — | `grudge_rule` |

## パラメータ

| 記号 | 定義域 | 説明 | 参照 |
|------|--------|------|------|
| $K$ | $\mathbb{N}_0$ | 遺恨ルールの数 | `NUM_GRUDGE_RULES` |

## 集合

| 記号 | 全要素 | 説明 | 参照 |
|------|------|------|------|
| $\mathcal{K}$ | $\{1, 2, \ldots, K\}$ | 遺恨ルールのインデックス集合 | `grudge_rule_indices` |
| $\mathcal{H}_k$ | $\mathcal{H}_k \subseteq \mathcal{I}$（$k \in \mathcal{K}$） | 遺恨のある組み合わせ。例: $\mathcal{H}_1 = \{\text{wolf}, \text{goat}\}$，$\mathcal{H}_2 = \{\text{goat}, \text{cabbage}\}$ | `grudge_members[k]` |
| $\mathcal{G}_k$ | $\mathcal{G}_k \subseteq \mathcal{I}$（$k \in \mathcal{K}$） | 遺恨組 $\mathcal{H}_k$ のメンバーが同じ地点にいるとき、その地点にいなければならない仲裁対象の集合。例: $\mathcal{G}_1 = \mathcal{G}_2 = \{\text{farmer}\}$ | `grudge_guardians[k]` |
| $\mathcal{P}$ | $\mathcal{P} \subseteq \mathcal{I}$ | 輸送手段を操縦できる対象の集合。例: $\mathcal{P} = \{\text{farmer}\}$ | `pilots` |

ルール $k \in \mathcal{K}$ ごとに仲裁対象集合 $\mathcal{G}_k$ が与えられる。$\mathcal{P}$ と $\mathcal{G}_k$ は一般に異なる集合であり、同一の対象が両方に含まれることもある。

## 目的関数

移動完了までの時間ステップを最小化する:

$$
\text{minimize} \quad T^{\text{max}} - \sum_{t \in \mathcal{T}} f_t + 2
$$

## 制約

[common.md の制約](common.md#制約) に加え、classic では次を課す。

### 遺恨組の仲裁

各 $k \in \mathcal{K}$ について、$\mathcal{H}_k$ のメンバーが同じ地点にいるときは、$\mathcal{G}_k$ の誰か 1 人がその地点にいなければならない。  
地点は出発側・到達側・移動中のいずれも対象とし、各ステップ $t \in \mathcal{T}$ について次が成り立つ:

$$
\sum_{i \in \mathcal{H}_k} \delta_{i,t}^{\text{start}} = |\mathcal{H}_k|
\quad \Rightarrow \quad
\sum_{g \in \mathcal{G}_k} \delta_{g,t}^{\text{start}} \geq 1
$$

$$
\sum_{i \in \mathcal{H}_k} \delta_{i,t}^{\text{goal}} = |\mathcal{H}_k|
\quad \Rightarrow \quad
\sum_{g \in \mathcal{G}_k} \delta_{g,t}^{\text{goal}} \geq 1
$$

$$
\sum_{i \in \mathcal{H}_k} \delta_{i,t}^{\text{transit}} = |\mathcal{H}_k|
\quad \Rightarrow \quad
\sum_{g \in \mathcal{G}_k} \delta_{g,t}^{\text{transit}} \geq 1
$$

線形計画では次のように記述する:

$$
\sum_{i \in \mathcal{H}_k} \delta_{i,t}^{\text{start}} - |\mathcal{H}_k| + 1
\leq \sum_{g \in \mathcal{G}_k} \delta_{g,t}^{\text{start}}
\quad (\forall k \in \mathcal{K},\, \forall t \in \mathcal{T})
\tag{C6-1}
$$

$$
\sum_{i \in \mathcal{H}_k} \delta_{i,t}^{\text{goal}} - |\mathcal{H}_k| + 1
\leq \sum_{g \in \mathcal{G}_k} \delta_{g,t}^{\text{goal}}
\quad (\forall k \in \mathcal{K},\, \forall t \in \mathcal{T})
\tag{C6-2}
$$

$$
\sum_{i \in \mathcal{H}_k} \delta_{i,t}^{\text{transit}} - |\mathcal{H}_k| + 1
\leq \sum_{g \in \mathcal{G}_k} \delta_{g,t}^{\text{transit}}
\quad (\forall k \in \mathcal{K},\, \forall t \in \mathcal{T})
\tag{C6-3}
$$

$|\mathcal{H}_k| = 2$ のときは、遺恨のある 2 対象が同じ地点にいる場合に仲裁対象が必要になる、と読める。

### 操船者

奇数ステップ（移動中）では、$\mathcal{P}$ の誰か 1 人が移動中にいなければならない:

$$
\sum_{p \in \mathcal{P}} \delta_{p,t}^{\text{transit}} \geq 1
\quad (\forall t \in \mathcal{T}^{\text{odd}})
\tag{C7-1}
$$
