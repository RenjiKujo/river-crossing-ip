# 川渡りパズル定式化（dr_stone）

**Languages:** [English](dr_stone.md) | [日本語](dr_stone.ja.md)

`puzzle_type: dr_stone` 向けの追加定式化。共通骨格は [common.ja.md](common.ja.md)、ルールの説明は [../README.ja.md](../README.ja.md#dr_stone) を参照。

インデックス・決定変数は [common.ja.md](common.ja.md) に従う。以下は dr_stone 固有のパラメータ・集合・目的関数・制約を記す。

## パラメータ

| 記号 | 定義域 | 説明 | 参照 |
|------|--------|------|------|
| $W_i$ | $\mathbb{R}_{\geq 0}$（$i \in \mathcal{I}$） | 対象 $i$ の重量 | `item_weight[i]` |
| $W^{\text{max}}$ | $\mathbb{R}_{> 0}$ | 輸送手段の最大積載重量 | `max_load_weight` |
| $A$ | $\mathbb{R}_{\geq 0}$ | 積載重量上限 $\eta$ のペナルティ係数 | `ALPHA` |
| $B$ | $\mathbb{R}_{\geq 0}$ | 移動時重量合計 $\zeta$ のペナルティ係数 | `BETA` |

## 集合

| 記号 | 全要素 | 説明 | 参照 |
|------|------|------|------|
| $\mathcal{S}^{\text{sus}}$ | $\mathcal{S}^{\text{sus}} \subseteq \mathcal{I}$ | 疑いありメンバーの集合。例: $\mathcal{S}^{\text{sus}} = \{\text{hyoga}, \text{zeno}\}$ | `suspicious_members` |
| $\mathcal{C}$ | $\mathcal{C} \subseteq \mathcal{I}$ | クラフトメンバーの集合。例: $\mathcal{C} = \{\text{senku}, \text{kaseki}, \text{chrome}, \text{zeno}\}$ | `craft_members` |
| $\mathcal{C}^{\text{sus}}$ | $\mathcal{C}^{\text{sus}} = \mathcal{C} \cap \mathcal{S}^{\text{sus}}$ | 疑いありクラフトメンバーの集合 | `suspicious_craft_members` |
| $\mathcal{C}^{\text{trusted}}$ | $\mathcal{C}^{\text{trusted}} = \mathcal{C} \setminus \mathcal{S}^{\text{sus}}$ | 疑いなしクラフトメンバーの集合 | `trusted_craft_members` |
| $\mathcal{B}$ | $\mathcal{B} \subseteq \mathcal{I}$ | バトルメンバーの集合。例: $\mathcal{B} = \{\text{tsukasa}, \text{kohaku}, \text{taiju}, \text{hyoga}\}$ | `battle_members` |
| $\mathcal{B}^{\text{sus}}$ | $\mathcal{B}^{\text{sus}} = \mathcal{B} \cap \mathcal{S}^{\text{sus}}$ | 疑いありバトルメンバーの集合 | `suspicious_battle_members` |
| $\mathcal{B}^{\text{trusted}}$ | $\mathcal{B}^{\text{trusted}} = \mathcal{B} \setminus \mathcal{S}^{\text{sus}}$ | 疑いなしバトルメンバーの集合 | `trusted_battle_members` |
| $\mathcal{Q}$ | $\mathcal{Q} \subseteq \mathcal{I}$ | 准バトルメンバー（思春期を超えた男）。例: $\mathcal{Q} = \{\text{senku}, \text{zeno}, \text{kaseki}, \text{gen}, \text{chrome}, \text{ukyo}, \text{ryusui}, \text{max}, \text{carlos}\}$ | `quasi_battle_members` |
| $\mathcal{Q}^{\text{sus}}$ | $\mathcal{Q}^{\text{sus}} = \mathcal{Q} \cap \mathcal{S}^{\text{sus}}$ | 疑いあり准バトルメンバー | `suspicious_quasi_battle_members` |
| $\mathcal{Q}^{\text{trusted}}$ | $\mathcal{Q}^{\text{trusted}} = \mathcal{Q} \setminus \mathcal{S}^{\text{sus}}$ | 疑いなし准バトルメンバー | `trusted_quasi_battle_members` |

$\mathcal{S}^{\text{sus}}$、$\mathcal{C}$、$\mathcal{B}$、$\mathcal{Q}$ は問題ごとに定義する。$\mathcal{C}^{\text{sus}}$、$\mathcal{C}^{\text{trusted}}$、$\mathcal{B}^{\text{sus}}$、$\mathcal{B}^{\text{trusted}}$、$\mathcal{Q}^{\text{sus}}$、$\mathcal{Q}^{\text{trusted}}$ はそこから導く。

## 決定変数

[common.ja.md の決定変数](common.ja.md#決定変数) に加え、dr_stone では次を用いる:

| 変数 | 定義域 | 意味 | 参照 |
|------|--------|------|------|
| $\eta$ | $\mathbb{R}_{\geq 0}$ | 各奇数ステップの積載重量の共通上限（スカラー） | `load_ceiling` |
| $\zeta$ | $\mathbb{R}_{\geq 0}$ | 全奇数ステップにおける積載重量の合計 | `total_load` |
| $b_t^{\text{start}}$ | $\{0, 1\}$ | ステップ $t$ の出発側に疑いありバトルメンバーが 1 人以上いるとき 1 | `suspicious_battle_present_start` |
| $b_t^{\text{goal}}$ | $\{0, 1\}$ | ステップ $t$ の到達側に疑いありバトルメンバーが 1 人以上いるとき 1 | `suspicious_battle_present_goal` |
| $q_t^{\text{start}}$ | $\{0, 1\}$ | ステップ $t$ の出発側に疑いあり准バトルメンバーが 1 人以上いるとき 1 | `suspicious_quasi_battle_present_start` |
| $q_t^{\text{goal}}$ | $\{0, 1\}$ | ステップ $t$ の到達側に疑いあり准バトルメンバーが 1 人以上いるとき 1 | `suspicious_quasi_battle_present_goal` |

## 目的関数

移動完了までの時間ステップを最小化しつつ、積載重量の上限ぎりぎり利用と無駄な往復移動を抑える:

$$
\text{minimize} \quad
T^{\text{max}} - \sum_{t \in \mathcal{T}} f_t + 2
+ A \eta + B \zeta
$$

$A \eta$ は各移動で $W^{\text{max}}$ 付近まで載せることを抑え、$B \zeta$ は移動ごとの重量合計（往復の多さ）を抑える。

## 制約

[common.ja.md の制約](common.ja.md#制約) に加え、dr_stone では次を課す。

### 重量定員

奇数ステップ $t \in \mathcal{T}^{\text{odd}}$ の積載重量は、共通の上限 $\eta$ より小さく、$\eta$ は $W^{\text{max}}$ より小さい:

$$
\sum_{i \in \mathcal{I}} W_i \, \delta_{i,t}^{\text{transit}} \leq \eta
\quad (\forall t \in \mathcal{T}^{\text{odd}})
\tag{C6-1}
$$

$$
\eta \leq W^{\text{max}}
\tag{C6-2}
$$

全奇数ステップの積載重量合計を $\zeta$ で表す:

$$
\zeta = \sum_{t \in \mathcal{T}^{\text{odd}}} \sum_{i \in \mathcal{I}} W_i \, \delta_{i,t}^{\text{transit}}
\tag{C6-3}
$$

[common.ja.md の人数定員](common.ja.md#人数定員)（C5-1）と併用する。

### 移動中の疑いありメンバーの監視

移動ステップ $t \in \mathcal{T}^{\text{odd}}$ について、移動中の疑いありメンバー数は疑いなしバトルメンバー数を超えない:

$$
\sum_{i \in \mathcal{S}^{\text{sus}}} \delta_{i,t}^{\text{transit}}
\leq \sum_{i \in \mathcal{B}^{\text{trusted}}} \delta_{i,t}^{\text{transit}}
\quad (\forall t \in \mathcal{T}^{\text{odd}})
\tag{C8-1}
$$

### 疑いありバトルメンバーの抑制

出発側・到達側それぞれについて、疑いありバトルメンバーが 1 人以上いるときのみ、疑いなしバトルメンバー数は疑いありバトルメンバー数より少なくとも 1 人多い必要がある。

まず、出発側・到達側の疑いありバトルメンバー存在フラグ $b_t^{\text{start}}$, $b_t^{\text{goal}}$ を定義する。  
$|\mathcal{B}^{\text{sus}}|$ は疑いありバトルメンバー数とする。

出発側及び到達側では、疑いありバトルメンバーが 1 人以上いることとフラグが 1 であることは必要十分である:

$$
b_t^{\text{start}} = 1
\quad \Leftrightarrow \quad
\sum_{i \in \mathcal{B}^{\text{sus}}} \delta_{i,t}^{\text{start}} \geq 1
\quad (\forall t \in \mathcal{T})
$$


$$
b_t^{\text{goal}} = 1
\quad \Leftrightarrow \quad
\sum_{i \in \mathcal{B}^{\text{sus}}} \delta_{i,t}^{\text{goal}} \geq 1
\quad (\forall t \in \mathcal{T})
$$

線形計画では次のように記述する:

$$
\sum_{i \in \mathcal{B}^{\text{sus}}} \delta_{i,t}^{\text{start}}
\geq b_t^{\text{start}}
\quad (\forall t \in \mathcal{T})
\tag{C9-1}
$$

$$
\sum_{i \in \mathcal{B}^{\text{sus}}} \delta_{i,t}^{\text{start}}
\leq |\mathcal{B}^{\text{sus}}| \, b_t^{\text{start}}
\quad (\forall t \in \mathcal{T})
\tag{C9-2}
$$

$$
\sum_{i \in \mathcal{B}^{\text{sus}}} \delta_{i,t}^{\text{goal}}
\geq b_t^{\text{goal}}
\quad (\forall t \in \mathcal{T})
\tag{C9-3}
$$

$$
\sum_{i \in \mathcal{B}^{\text{sus}}} \delta_{i,t}^{\text{goal}}
\leq |\mathcal{B}^{\text{sus}}| \, b_t^{\text{goal}}
\quad (\forall t \in \mathcal{T})
\tag{C9-4}
$$

C9-1, C9-2 により $b_t^{\text{start}} = 0$ のとき疑いありバトルメンバーは出発側にいない。C9-3, C9-4 も到達側で同様である。

フラグが 1 のとき、元の抑制制約が成り立つ:

$$
b_t^{\text{start}} = 1
\quad \Rightarrow \quad
\sum_{i \in \mathcal{B}^{\text{sus}}} \delta_{i,t}^{\text{start}} + 1
\leq \sum_{i \in \mathcal{B}^{\text{trusted}}} \delta_{i,t}^{\text{start}}
\quad (\forall t \in \mathcal{T})
$$

$$
b_t^{\text{goal}} = 1
\quad \Rightarrow \quad
\sum_{i \in \mathcal{B}^{\text{sus}}} \delta_{i,t}^{\text{goal}} + 1
\leq \sum_{i \in \mathcal{B}^{\text{trusted}}} \delta_{i,t}^{\text{goal}}
\quad (\forall t \in \mathcal{T})
$$

線形計画では次のように記述する（$M$ は十分大きい定数。実装では $|\mathcal{I}|$ を用いる）:

$$
\sum_{i \in \mathcal{B}^{\text{sus}}} \delta_{i,t}^{\text{start}} + 1
\leq \sum_{i \in \mathcal{B}^{\text{trusted}}} \delta_{i,t}^{\text{start}}
+ M \left(1 - b_t^{\text{start}}\right)
\quad (\forall t \in \mathcal{T})
\tag{C9-5}
$$

$$
\sum_{i \in \mathcal{B}^{\text{sus}}} \delta_{i,t}^{\text{goal}} + 1
\leq \sum_{i \in \mathcal{B}^{\text{trusted}}} \delta_{i,t}^{\text{goal}}
+ M \left(1 - b_t^{\text{goal}}\right)
\quad (\forall t \in \mathcal{T})
\tag{C9-6}
$$

### 疑いあり准バトルメンバーの抑制

出発側・到達側それぞれについて、疑いあり准バトルメンバーが 1 人以上いるときのみ、疑いなし准バトルメンバー数は疑いあり准バトルメンバー数より少なくとも 3 人多い必要がある。

まず、出発側・到達側の疑いあり准バトルメンバー存在フラグ $q_t^{\text{start}}$, $q_t^{\text{goal}}$ を定義する。  
$|\mathcal{Q}^{\text{sus}}|$ は疑いあり准バトルメンバー数とする。

出発側及び到達側では、疑いあり准バトルメンバーが 1 人以上いることとフラグが 1 であることは必要十分である:

$$
q_t^{\text{start}} = 1
\quad \Leftrightarrow \quad
\sum_{i \in \mathcal{Q}^{\text{sus}}} \delta_{i,t}^{\text{start}} \geq 1
\quad (\forall t \in \mathcal{T})
$$


$$
q_t^{\text{goal}} = 1
\quad \Leftrightarrow \quad
\sum_{i \in \mathcal{Q}^{\text{sus}}} \delta_{i,t}^{\text{goal}} \geq 1
\quad (\forall t \in \mathcal{T})
$$

線形計画では次のように記述する:

$$
\sum_{i \in \mathcal{Q}^{\text{sus}}} \delta_{i,t}^{\text{start}}
\geq q_t^{\text{start}}
\quad (\forall t \in \mathcal{T})
\tag{C10-1}
$$

$$
\sum_{i \in \mathcal{Q}^{\text{sus}}} \delta_{i,t}^{\text{start}}
\leq |\mathcal{Q}^{\text{sus}}| \, q_t^{\text{start}}
\quad (\forall t \in \mathcal{T})
\tag{C10-2}
$$

$$
\sum_{i \in \mathcal{Q}^{\text{sus}}} \delta_{i,t}^{\text{goal}}
\geq q_t^{\text{goal}}
\quad (\forall t \in \mathcal{T})
\tag{C10-3}
$$

$$
\sum_{i \in \mathcal{Q}^{\text{sus}}} \delta_{i,t}^{\text{goal}}
\leq |\mathcal{Q}^{\text{sus}}| \, q_t^{\text{goal}}
\quad (\forall t \in \mathcal{T})
\tag{C10-4}
$$

C10-1, C10-2 により $q_t^{\text{start}} = 0$ のとき疑いあり准バトルメンバーは出発側にいない。C10-3, C10-4 も到達側で同様である。

フラグが 1 のとき、元の抑制制約が成り立つ:

$$
q_t^{\text{start}} = 1
\quad \Rightarrow \quad
\sum_{i \in \mathcal{Q}^{\text{sus}}} \delta_{i,t}^{\text{start}} + 3
\leq \sum_{i \in \mathcal{Q}^{\text{trusted}}} \delta_{i,t}^{\text{start}}
\quad (\forall t \in \mathcal{T})
$$

$$
q_t^{\text{goal}} = 1
\quad \Rightarrow \quad
\sum_{i \in \mathcal{Q}^{\text{sus}}} \delta_{i,t}^{\text{goal}} + 3
\leq \sum_{i \in \mathcal{Q}^{\text{trusted}}} \delta_{i,t}^{\text{goal}}
\quad (\forall t \in \mathcal{T})
$$

線形計画では次のように記述する（$M$ は十分大きい定数。実装では $|\mathcal{I}|$ を用いる）:

$$
\sum_{i \in \mathcal{Q}^{\text{sus}}} \delta_{i,t}^{\text{start}} + 3
\leq \sum_{i \in \mathcal{Q}^{\text{trusted}}} \delta_{i,t}^{\text{start}}
+ M \left(1 - q_t^{\text{start}}\right)
\quad (\forall t \in \mathcal{T})
\tag{C10-5}
$$

$$
\sum_{i \in \mathcal{Q}^{\text{sus}}} \delta_{i,t}^{\text{goal}} + 3
\leq \sum_{i \in \mathcal{Q}^{\text{trusted}}} \delta_{i,t}^{\text{goal}}
+ M \left(1 - q_t^{\text{goal}}\right)
\quad (\forall t \in \mathcal{T})
\tag{C10-6}
$$

### 最終移動の構成

[README の最終移動ルール](../README.ja.md#dr_stone) より、全員が到達側にいる状態の直前ステップで移動中のメンバーには、疑いなしクラフトメンバーと疑いなしバトルメンバーが各 1 人以上必要である。

フィニッシュは [common.ja.md のフィニッシュフラグ](common.ja.md#フィニッシュフラグ)（C4）により単調に立ち上がる。したがって、初めて $f_t = 1$ となるステップ $t$ では $f_t - f_{t-1} = 1$ であり、それ以外では $0$ である（$t \in \{1, 2, \ldots, T^{\text{max}}\}$）。その $t$ の直前ステップ $t-1$ が最終移動である。

論理形:

$$
f_t - f_{t-1} = 1
\quad \Rightarrow \quad
\sum_{i \in \mathcal{C}^{\text{trusted}}} \delta_{i,t-1}^{\text{transit}} \geq 1
\quad (\forall t \in \{1, 2, \ldots, T^{\text{max}}\})
$$

$$
f_t - f_{t-1} = 1
\quad \Rightarrow \quad
\sum_{i \in \mathcal{B}^{\text{trusted}}} \delta_{i,t-1}^{\text{transit}} \geq 1
\quad (\forall t \in \{1, 2, \ldots, T^{\text{max}}\})
$$

右辺を $f_t - f_{t-1}$ に置き換えると、含意は次の線形不等式と等価である（$f_t = f_{t-1}$ のときは自明、$f_t - f_{t-1} = 1$ のときだけ人数下限が効く）:

$$
\sum_{i \in \mathcal{C}^{\text{trusted}}} \delta_{i,t-1}^{\text{transit}}
\geq f_t - f_{t-1}
\quad (\forall t \in \{1, 2, \ldots, T^{\text{max}}\})
\tag{C11-1}
$$

$$
\sum_{i \in \mathcal{B}^{\text{trusted}}} \delta_{i,t-1}^{\text{transit}}
\geq f_t - f_{t-1}
\quad (\forall t \in \{1, 2, \ldots, T^{\text{max}}\})
\tag{C11-2}
$$

補足:

- 初回フィニッシュは偶数ステップにしか起きない（奇数ステップでは移動中の対象が到達側にいないため）。そのとき $t-1$ は奇数の移動ステップである。
- $f_0 = 1$（初期から全員到達側）のときは差分が常に $0$ となり、本制約は無効化される。
