# River-crossing formulation (classic)

**Languages:** [English](classic.md) | [日本語](classic.ja.md)

Extra formulation for `puzzle_type: classic`. Shared skeleton: [common.md](common.md). Rule narrative: [../README.md](../README.md#classic).

Indices and decision variables follow [common.md](common.md). Below are classic-only indices, parameters, sets, objective, and constraints.

## Indices

| Symbol | Domain | Description | Unit | Code |
|--------|--------|-------------|------|------|
| $k$ | $\mathcal{K}$ | Grudge-rule index | — | `grudge_rule` |

## Parameters

| Symbol | Domain | Description | Code |
|--------|--------|-------------|------|
| $K$ | $\mathbb{N}_0$ | Number of grudge rules | `NUM_GRUDGE_RULES` |

## Sets

| Symbol | Elements | Description | Code |
|--------|----------|-------------|------|
| $\mathcal{K}$ | $\{1, 2, \ldots, K\}$ | Index set of grudge rules | `grudge_rule_indices` |
| $\mathcal{H}_k$ | $\mathcal{H}_k \subseteq \mathcal{I}$ ($k \in \mathcal{K}$) | Forbidden co-presence set. E.g. $\mathcal{H}_1 = \{\text{wolf}, \text{goat}\}$, $\mathcal{H}_2 = \{\text{goat}, \text{cabbage}\}$ | `grudge_members[k]` |
| $\mathcal{G}_k$ | $\mathcal{G}_k \subseteq \mathcal{I}$ ($k \in \mathcal{K}$) | Guardians who must be present when $\mathcal{H}_k$ shares a location. E.g. $\mathcal{G}_1 = \mathcal{G}_2 = \{\text{farmer}\}$ | `grudge_guardians[k]` |
| $\mathcal{P}$ | $\mathcal{P} \subseteq \mathcal{I}$ | Items that can operate the vehicle. E.g. $\mathcal{P} = \{\text{farmer}\}$ | `pilots` |

Each rule $k \in \mathcal{K}$ has its own guardian set $\mathcal{G}_k$. $\mathcal{P}$ and $\mathcal{G}_k$ are distinct sets in general; the same item may belong to both.

## Objective

Minimize time steps until completion:

$$
\text{minimize} \quad T^{\text{max}} - \sum_{t \in \mathcal{T}} f_t + 2
$$

## Constraints

In addition to the [shared constraints](common.md#constraints), classic adds the following.

### Guardians for grudge sets

For each $k \in \mathcal{K}$, when every member of $\mathcal{H}_k$ shares a location, at least one member of $\mathcal{G}_k$ must be at that location.  
This applies to start side, goal side, and transit, for every step $t \in \mathcal{T}$:

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

In linear form:

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

When $|\mathcal{H}_k| = 2$, this reads as: if the two grudging items share a location, a guardian is required.

### Pilots

On odd steps (in transit), at least one pilot from $\mathcal{P}$ must be in transit:

$$
\sum_{p \in \mathcal{P}} \delta_{p,t}^{\text{transit}} \geq 1
\quad (\forall t \in \mathcal{T}^{\text{odd}})
\tag{C7-1}
$$
