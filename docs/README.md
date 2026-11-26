# River-crossing puzzle notes

**Languages:** [English](README.md) | [日本語](README.ja.md)

## Problem setup

### Shared (all `puzzle_type`s)

**Given capacity and safety constraints, how should a group move from one place to another so that everyone arrives safely in the fewest steps?**

We cast that question as transporting items across three states: start side, goal side, and in transit. This repository instantiates it as follows:

- Locations are start side, goal side, and in transit.
- There is a limit on how many items can move at once.
- Step 0 is the initial placement. Not everyone need start on the start side.
- From step 1 onward, “move” and “board/alight” alternate.
  - Odd steps: the vehicle moves from one side to the other (occupants are in transit).
  - Even steps: boarding and alighting occur.
- The goal is that every item is on the goal side.
- The objective is to minimize the number of time steps until completion.

### classic

Canonical instance:

- Items are farmer, wolf, goat, and cabbage.
- At the initial step, everyone is on the start side.
- While a forbidden pair shares a location, the farmer must be at that same location.
- Only the farmer can operate the boat alone.

### dr_stone

Interpretation based on the manga:

- Models ropeway travel in the Andes from *Dr. Stone* (South America arc).
- Some members start on the goal side (Kohaku).
- There is also a weight-based load limit.
- Member sets include:
  - Suspicious members (e.g. Hyoga, Xeno)
  - Craft members (e.g. Senku, Kaseki, Chrome, Xeno)
  - Battle members (e.g. Tsukasa, Kohaku, Taiju, Hyoga)
- At each location, the number of trusted battle members must be at least the number of suspicious members present.
- While suspicious battle members are on the start or goal side, trusted battle members at that location must strictly outnumber them.
- On the final move (the step just before everyone is on the goal side), the transit party needs at least one trusted craft member and at least one trusted battle member.

## Files

| File | Content |
|------|---------|
| [yaml_spec.md](yaml_spec.md) | How to write problem-definition YAML |
| [formulation/common.md](formulation/common.md) | Shared IP skeleton (↔ `engine.py`) |
| [formulation/classic.md](formulation/classic.md) | classic extras (↔ `constraints/classic.py`) |
| [formulation/dr_stone.md](formulation/dr_stone.md) | dr_stone extras (↔ `constraints/dr_stone.py`) |
