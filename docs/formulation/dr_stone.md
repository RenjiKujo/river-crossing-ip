# River-crossing formulation (dr_stone)

**Languages:** [English](dr_stone.md) | [日本語](dr_stone.ja.md)

Extra formulation for `puzzle_type: dr_stone`. Shared skeleton: [common.md](common.md). Rule narrative: [../README.md](../README.md#dr_stone).

Indices and decision variables follow [common.md](common.md). Below are dr_stone-only parameters, sets, variables, objective, and constraints.

## Parameters

| Symbol | Domain | Description | Code |
|--------|--------|-------------|------|
| $W_i$ | $\mathbb{R}_{\geq 0}$ ($i \in \mathcal{I}$) | Weight of item $i$ | `item_weight[i]` |
| $W^{\text{max}}$ | $\mathbb{R}_{> 0}$ | Maximum vehicle load weight | `max_load_weight` |
| $A$ | $\mathbb{R}_{\geq 0}$ | Penalty coefficient on load ceiling $\eta$ | `ALPHA` |
| $B$ | $\mathbb{R}_{\geq 0}$ | Penalty coefficient on total transit weight $\zeta$ | `BETA` |

## Sets

| Symbol | Elements | Description | Code |
|--------|----------|-------------|------|
| $\mathcal{S}^{\text{sus}}$ | $\mathcal{S}^{\text{sus}} \subseteq \mathcal{I}$ | Suspicious members. E.g. $\mathcal{S}^{\text{sus}} = \{\text{hyoga}, \text{zeno}\}$ | `suspicious_members` |
| $\mathcal{C}$ | $\mathcal{C} \subseteq \mathcal{I}$ | Craft members. E.g. $\mathcal{C} = \{\text{senku}, \text{kaseki}, \text{chrome}, \text{zeno}\}$ | `craft_members` |
| $\mathcal{C}^{\text{sus}}$ | $\mathcal{C}^{\text{sus}} = \mathcal{C} \cap \mathcal{S}^{\text{sus}}$ | Suspicious craft members | `suspicious_craft_members` |
| $\mathcal{C}^{\text{trusted}}$ | $\mathcal{C}^{\text{trusted}} = \mathcal{C} \setminus \mathcal{S}^{\text{sus}}$ | Trusted craft members | `trusted_craft_members` |
| $\mathcal{B}$ | $\mathcal{B} \subseteq \mathcal{I}$ | Battle members. E.g. $\mathcal{B} = \{\text{tsukasa}, \text{kohaku}, \text{taiju}, \text{hyoga}\}$ | `battle_members` |
| $\mathcal{B}^{\text{sus}}$ | $\mathcal{B}^{\text{sus}} = \mathcal{B} \cap \mathcal{S}^{\text{sus}}$ | Suspicious battle members | `suspicious_battle_members` |
| $\mathcal{B}^{\text{trusted}}$ | $\mathcal{B}^{\text{trusted}} = \mathcal{B} \setminus \mathcal{S}^{\text{sus}}$ | Trusted battle members | `trusted_battle_members` |
| $\mathcal{Q}$ | $\mathcal{Q} \subseteq \mathcal{I}$ | Quasi-battle members (adult males past adolescence). E.g. $\mathcal{Q} = \{\text{senku}, \text{zeno}, \text{kaseki}, \text{gen}, \text{chrome}, \text{ukyo}, \text{ryusui}, \text{max}, \text{carlos}\}$ | `quasi_battle_members` |
| $\mathcal{Q}^{\text{sus}}$ | $\mathcal{Q}^{\text{sus}} = \mathcal{Q} \cap \mathcal{S}^{\text{sus}}$ | Suspicious quasi-battle members | `suspicious_quasi_battle_members` |
| $\mathcal{Q}^{\text{trusted}}$ | $\mathcal{Q}^{\text{trusted}} = \mathcal{Q} \setminus \mathcal{S}^{\text{sus}}$ | Trusted quasi-battle members | `trusted_quasi_battle_members` |

$\mathcal{S}^{\text{sus}}$, $\mathcal{C}$, $\mathcal{B}$, and $\mathcal{Q}$ are instance-defined. $\mathcal{C}^{\text{sus}}$, $\mathcal{C}^{\text{trusted}}$, $\mathcal{B}^{\text{sus}}$, $\mathcal{B}^{\text{trusted}}$, $\mathcal{Q}^{\text{sus}}$, and $\mathcal{Q}^{\text{trusted}}$ are derived from them.

## Decision variables

In addition to the [shared variables](common.md#decision-variables), dr_stone uses:

| Variable | Domain | Meaning | Code |
|----------|--------|---------|------|
| $\eta$ | $\mathbb{R}_{\geq 0}$ | Shared load-weight ceiling across odd steps (scalar) | `load_ceiling` |
| $\zeta$ | $\mathbb{R}_{\geq 0}$ | Sum of load weights over all odd steps | `total_load` |
| $b_t^{\text{start}}$ | $\{0, 1\}$ | 1 if at least one suspicious battle member is on the start side at step $t$ | `suspicious_battle_present_start` |
| $b_t^{\text{goal}}$ | $\{0, 1\}$ | 1 if at least one suspicious battle member is on the goal side at step $t$ | `suspicious_battle_present_goal` |
| $q_t^{\text{start}}$ | $\{0, 1\}$ | 1 if at least one suspicious quasi-battle member is on the start side at step $t$ | `suspicious_quasi_battle_present_start` |
| $q_t^{\text{goal}}$ | $\{0, 1\}$ | 1 if at least one suspicious quasi-battle member is on the goal side at step $t$ | `suspicious_quasi_battle_present_goal` |

## Objective

Minimize completion time while discouraging near-max loads and unnecessary round trips:

$$
\text{minimize} \quad
T^{\text{max}} - \sum_{t \in \mathcal{T}} f_t + 2
+ A \eta + B \zeta
$$

$A \eta$ penalizes loading near $W^{\text{max}}$; $B \zeta$ penalizes total transit weight (proxy for extra trips).

## Constraints

In addition to the [shared constraints](common.md#constraints), dr_stone adds the following.

### Weight capacity

On each odd step $t \in \mathcal{T}^{\text{odd}}$, the load weight is at most the shared ceiling $\eta$, and $\eta$ is at most $W^{\text{max}}$:

$$
\sum_{i \in \mathcal{I}} W_i \, \delta_{i,t}^{\text{transit}} \leq \eta
\quad (\forall t \in \mathcal{T}^{\text{odd}})
\tag{C6-1}
$$

$$
\eta \leq W^{\text{max}}
\tag{C6-2}
$$

Total load weight over all odd steps is $\zeta$:

$$
\zeta = \sum_{t \in \mathcal{T}^{\text{odd}}} \sum_{i \in \mathcal{I}} W_i \, \delta_{i,t}^{\text{transit}}
\tag{C6-3}
$$

Used together with the [shared passenger capacity](common.md#passenger-capacity) (C5-1).

### Escorting suspicious members in transit

On transit steps $t \in \mathcal{T}^{\text{odd}}$, the number of suspicious members in transit does not exceed the number of trusted battle members in transit:

$$
\sum_{i \in \mathcal{S}^{\text{sus}}} \delta_{i,t}^{\text{transit}}
\leq \sum_{i \in \mathcal{B}^{\text{trusted}}} \delta_{i,t}^{\text{transit}}
\quad (\forall t \in \mathcal{T}^{\text{odd}})
\tag{C8-1}
$$

### Suppressing suspicious battle members

On the start and goal sides, only when at least one suspicious battle member is present must trusted battle members strictly outnumber them by at least one.

First define presence flags $b_t^{\text{start}}$, $b_t^{\text{goal}}$.  
$|\mathcal{B}^{\text{sus}}|$ is the number of suspicious battle members.

On each side, the flag is 1 if and only if at least one suspicious battle member is present:

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

In linear form:

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

By C9-1 and C9-2, $b_t^{\text{start}} = 0$ implies no suspicious battle member is on the start side. C9-3 and C9-4 are analogous for the goal side.

When the flag is 1, the suppression constraint holds:

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

In linear form ($M$ is a sufficiently large constant; the implementation uses $|\mathcal{I}|$):

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

### Suppressing suspicious quasi-battle members

On the start and goal sides, only when at least one suspicious quasi-battle member is present must trusted quasi-battle members outnumber them by at least three.

First define presence flags $q_t^{\text{start}}$, $q_t^{\text{goal}}$.  
$|\mathcal{Q}^{\text{sus}}|$ is the number of suspicious quasi-battle members.

On each side, the flag is 1 if and only if at least one suspicious quasi-battle member is present:

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

In linear form:

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

By C10-1 and C10-2, $q_t^{\text{start}} = 0$ implies no suspicious quasi-battle member is on the start side. C10-3 and C10-4 are analogous for the goal side.

When the flag is 1, the suppression constraint holds:

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

In linear form ($M$ is a sufficiently large constant; the implementation uses $|\mathcal{I}|$):

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

### Final-move composition

Per the [README final-move rule](../README.md#dr_stone), the transit party on the step immediately before everyone is on the goal side must include at least one trusted craft member and at least one trusted battle member.

Finish rises monotonically via the [shared finish flag](common.md#finish-flag) (C4). Thus the first step $t$ with $f_t = 1$ has $f_t - f_{t-1} = 1$, and otherwise the difference is $0$ ($t \in \{1, 2, \ldots, T^{\text{max}}\}$). That preceding step $t-1$ is the final move.

Logical form:

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

Replacing the right-hand side with $f_t - f_{t-1}$ yields equivalent linear inequalities (vacuous when $f_t = f_{t-1}$; the headcount lower bound binds only when $f_t - f_{t-1} = 1$):

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

Notes:

- The first finish can only occur on an even step (on odd steps someone in transit is not yet on the goal side). Then $t-1$ is an odd transit step.
- If $f_0 = 1$ (everyone already on the goal side initially), the difference is always $0$ and these constraints are inactive.
