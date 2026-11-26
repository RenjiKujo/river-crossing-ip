# River-crossing formulation (shared)

**Languages:** [English](common.md) | [日本語](common.ja.md)

Integer-programming skeleton independent of `puzzle_type`. For the rule narrative, see [../README.md](../README.md#problem-setup).

## Indices

| Symbol | Domain | Description | Unit | Code |
|--------|--------|-------------|------|------|
| $i$ | $\mathcal{I}$ | Item index | — | `item` |
| $t$ | $\mathcal{T}$ | Time step | step | `time_step` |

## Parameters

| Symbol | Domain | Description | Code |
|--------|--------|-------------|------|
| $T^{\text{max}}$ | $\mathbb{N}$ | Maximum time step | `MAX_TIME_STEP` |
| $T^{\text{buffer}}$ | $\mathbb{N}_0$ | Buffer on the time horizon | `BUFFER_TIME` |
| $C$ | $\mathbb{N}$ | Maximum passenger capacity | `MAX_CAPACITY` |

$T^{\text{max}}$ is given by:

$$
T^{\text{max}} = 4 \left( \left\lceil \frac{|\mathcal{I}|}{C} \right\rceil + T^{\text{buffer}} \right) + 2
$$


## Sets

| Symbol | Elements | Description | Code |
|--------|----------|-------------|------|
| $\mathcal{I}$ | instance-dependent | Set of items to move | `items` |
| $\mathcal{I}_0^{\text{goal}}$ | $\mathcal{I}_0^{\text{goal}} \subseteq \mathcal{I}$ (instance-dependent) | Items already on the goal side at step 0 | `initial_far_side_items` |
| $\mathcal{T}$ | $\{0, 1, \ldots, T^{\text{max}}\}$ | Set of time steps | `time_steps` |
| $\mathcal{T}^{\text{even}}$ | $\{0, 2, 4, \ldots, T^{\text{max}}\}$ | Even steps (step 0 is initial placement; later even steps are board/alight) | `even_time_steps` |
| $\mathcal{T}^{\text{odd}}$ | $\{1, 3, 5, \ldots, (T^{\text{max}}-1)\}$ | Odd steps (transit) | `odd_time_steps` |
| $\mathcal{T}^{4n+1}$ | $\{1, 5, 9, \ldots, (T^{\text{max}}-1)\}$ | Steps congruent to 1 mod 4 (start → goal transit) | `time_steps_4n_plus_1` |
| $\mathcal{T}^{4n+3}$ | $\{3, 7, 11, \ldots, (T^{\text{max}}-3)\}$ | Steps congruent to 3 mod 4 (goal → start transit) | `time_steps_4n_plus_3` |


## Decision variables

| Variable | Domain | Meaning | Code |
|----------|--------|---------|------|
| $\delta_{i,t}^{\text{start}}$ | $\{0, 1\}$ | 1 if item $i$ is on the start side at step $t$ | `delta_start` |
| $\delta_{i,t}^{\text{goal}}$ | $\{0, 1\}$ | 1 if item $i$ is on the goal side at step $t$ | `delta_goal` |
| $\delta_{i,t}^{\text{transit}}$ | $\{0, 1\}$ | 1 if item $i$ is in transit at step $t$ | `delta_transit` |
| $f_t$ | $\{0, 1\}$ | 1 if every item is on the goal side at step $t$ | `finish_flag` |

For the objective, see [classic.md](classic.md) or [dr_stone.md](dr_stone.md) by `puzzle_type`.

## Constraints

The following constraints apply for both `classic` and `dr_stone`.

### Location uniqueness

Every item occupies exactly one location at each time step:

$$
\delta_{i,t}^{\text{start}} + \delta_{i,t}^{\text{goal}} + \delta_{i,t}^{\text{transit}} = 1
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T})
\tag{C1-1}
$$

### State transitions

On even steps, no item is in transit:

$$
\delta_{i,t}^{\text{transit}} = 0
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{\text{even}})
\tag{C2-1}
$$

For $t \in \mathcal{T}^{4n+1}$ (start → goal transit), item $i$ being in transit at $t$ is equivalent to being on the start side at $t-1$ and on the goal side at $t+1$:

$$
\delta_{i,t}^{\text{transit}} = 1
\quad \Leftrightarrow \quad
\delta_{i,t-1}^{\text{start}} = 1 \;\wedge\; \delta_{i,t+1}^{\text{goal}} = 1
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{4n+1})
$$

In linear form:

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

For $t \in \mathcal{T}^{4n+3}$ (goal → start transit), item $i$ being in transit at $t$ is equivalent to being on the goal side at $t-1$ and on the start side at $t+1$:

$$
\delta_{i,t}^{\text{transit}} = 1
\quad \Leftrightarrow \quad
\delta_{i,t-1}^{\text{goal}} = 1 \;\wedge\; \delta_{i,t+1}^{\text{start}} = 1
\quad (\forall i \in \mathcal{I},\, \forall t \in \mathcal{T}^{4n+3})
$$

In linear form:

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

On a transit step $t \in \mathcal{T}^{\text{odd}}$, if item $i$ is not in transit, its start-side and goal-side locations are unchanged across $t-1$, $t$, and $t+1$:

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

In linear form:

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

### Initial state

At step $t=0$, only items in $\mathcal{I}_0^{\text{goal}}$ are on the goal side:

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

### Finish flag

At step $t$, the finish flag $f_t$ is 1 if and only if the sum of $\delta_{i,t}^{\text{goal}}$ equals $|\mathcal{I}|$:

$$
\sum_{i \in \mathcal{I}} \delta_{i,t}^{\text{goal}} = |\mathcal{I}| \quad \Leftrightarrow \quad f_t = 1
$$

In linear form:

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

Once finished, stay finished (and remain on the goal side):

$$
f_t \leq f_{t+1}
\quad (\forall t \in \{0, 1, \ldots, (T^{\text{max}} - 1)\})
\tag{C4-3}
$$

Completion must occur within the horizon:

$$
f_{T^{\text{max}}} = 1
\tag{C4-4}
$$

### Passenger capacity

$$
\sum_{i \in \mathcal{I}} \delta_{i,t}^{\text{transit}} \leq C
\quad (t \in \mathcal{T}^{\text{odd}})
\tag{C5-1}
$$
