"""問題定義 YAML の読み込み。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from river_crossing_ip.types import ClassicSpec, DrStoneSpec, GrudgeRule, PuzzleSpec


class SpecLoadError(ValueError):
    """問題定義 YAML の読み込み・検証エラー。"""


def load_spec(path: str | Path) -> PuzzleSpec:
    """YAML ファイルから問題定義を読み込む。

    Args:
      path: YAML ファイルパス。

    Returns:
      puzzle_type に応じた問題定義。

    Raises:
      SpecLoadError: ファイル読み込み失敗、必須キー欠落、検証失敗時。
      FileNotFoundError: ファイルが存在しない場合。
    """
    spec_path = Path(path)
    raw = _load_yaml(spec_path)
    puzzle_type = _require_str(raw, "puzzle_type")

    if puzzle_type == "classic":
        return _parse_classic(raw)
    if puzzle_type == "dr_stone":
        return _parse_dr_stone(raw)

    raise SpecLoadError(f"unsupported puzzle_type: {puzzle_type!r}")


def _load_yaml(path: Path) -> dict[str, Any]:
    """YAML を辞書として読み込む。"""
    if not path.is_file():
        raise FileNotFoundError(f"spec file not found: {path}")

    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise SpecLoadError(f"root of {path} must be a mapping")

    return data


def _parse_classic(raw: dict[str, Any]) -> ClassicSpec:
    """classic 用 YAML を ClassicSpec に変換する。"""
    items = _parse_items(raw)
    capacity = _require_positive_int(raw, "capacity")
    buffer_time = _require_non_negative_int(raw, "buffer_time", default=0)
    initial_far_side = _parse_name_set(raw, "initial_far_side", items, default=[])
    pilots = _parse_name_set(raw, "pilots", items)
    forbidden_co_presence = _parse_forbidden_co_presence(raw, items)

    return ClassicSpec(
        puzzle_type="classic",
        items=items,
        capacity=capacity,
        initial_far_side=initial_far_side,
        buffer_time=buffer_time,
        pilots=pilots,
        forbidden_co_presence=forbidden_co_presence,
    )


def _parse_dr_stone(raw: dict[str, Any]) -> DrStoneSpec:
    """dr_stone 用 YAML を DrStoneSpec に変換する。"""
    items = _parse_items(raw)
    capacity = _require_positive_int(raw, "capacity")
    buffer_time = _require_non_negative_int(raw, "buffer_time", default=0)
    initial_far_side = _parse_name_set(raw, "initial_far_side", items, default=[])
    item_weights = _parse_item_weights(raw, items)
    max_load_weight = _require_positive_float(raw, "max_load_weight")
    alpha = _require_non_negative_float(raw, "alpha", default=0.0)
    beta = _require_non_negative_float(raw, "beta", default=0.0)
    suspicious_members = _parse_name_set(raw, "suspicious_members", items, default=[])
    craft_members = _parse_name_set(raw, "craft_members", items, default=[])
    battle_members = _parse_name_set(raw, "battle_members", items, default=[])
    quasi_battle_members = _parse_name_set(
        raw,
        "quasi_battle_members",
        items,
        default=[],
    )

    return DrStoneSpec(
        puzzle_type="dr_stone",
        items=items,
        capacity=capacity,
        initial_far_side=initial_far_side,
        buffer_time=buffer_time,
        item_weights=item_weights,
        max_load_weight=max_load_weight,
        alpha=alpha,
        beta=beta,
        suspicious_members=suspicious_members,
        craft_members=craft_members,
        battle_members=battle_members,
        quasi_battle_members=quasi_battle_members,
    )


def _parse_items(raw: dict[str, Any]) -> tuple[str, ...]:
    """items リストを検証して tuple に変換する。"""
    if "items" not in raw:
        raise SpecLoadError("missing required key: items")

    value = raw["items"]
    if not isinstance(value, list) or not value:
        raise SpecLoadError("items must be a non-empty list")

    items: list[str] = []
    seen: set[str] = set()
    for entry in value:
        if not isinstance(entry, str) or not entry:
            raise SpecLoadError(f"each item must be a non-empty string, got {entry!r}")
        if entry in seen:
            raise SpecLoadError(f"duplicate item name: {entry!r}")
        seen.add(entry)
        items.append(entry)

    return tuple(items)


def _parse_name_set(
    raw: dict[str, Any],
    key: str,
    items: tuple[str, ...],
    *,
    default: list[str] | None = None,
) -> frozenset[str]:
    """items に含まれる名前の集合をパースする。"""
    if key not in raw:
        if default is None:
            raise SpecLoadError(f"missing required key: {key}")
        value = default
    else:
        value = raw[key]

    if not isinstance(value, list):
        raise SpecLoadError(f"{key} must be a list")

    item_set = set(items)
    names: set[str] = set()
    for entry in value:
        if not isinstance(entry, str) or not entry:
            raise SpecLoadError(f"each entry in {key} must be a non-empty string")
        if entry not in item_set:
            raise SpecLoadError(f"unknown item in {key}: {entry!r}")
        names.add(entry)

    return frozenset(names)


def _parse_forbidden_co_presence(
    raw: dict[str, Any],
    items: tuple[str, ...],
) -> tuple[GrudgeRule, ...]:
    """forbidden_co_presence を GrudgeRule の tuple に変換する。"""
    if "forbidden_co_presence" not in raw:
        raise SpecLoadError("missing required key: forbidden_co_presence")

    value = raw["forbidden_co_presence"]
    if not isinstance(value, list):
        raise SpecLoadError("forbidden_co_presence must be a list")

    item_set = set(items)
    rules: list[GrudgeRule] = []
    for index, entry in enumerate(value):
        if not isinstance(entry, dict):
            raise SpecLoadError(
                f"forbidden_co_presence[{index}] must be a mapping",
            )

        members = _parse_rule_name_list(entry, "members", item_set, index)
        guardians = _parse_rule_name_list(entry, "guardians", item_set, index)
        if not members:
            raise SpecLoadError(
                f"forbidden_co_presence[{index}].members must be non-empty",
            )
        if not guardians:
            raise SpecLoadError(
                f"forbidden_co_presence[{index}].guardians must be non-empty",
            )

        description = entry.get("description", "")
        if description is not None and not isinstance(description, str):
            raise SpecLoadError(
                f"forbidden_co_presence[{index}].description must be a string",
            )

        rules.append(
            GrudgeRule(
                members=frozenset(members),
                guardians=frozenset(guardians),
                description=description or "",
            ),
        )

    return tuple(rules)


def _parse_rule_name_list(
    entry: dict[str, Any],
    key: str,
    item_set: set[str],
    rule_index: int,
) -> list[str]:
    """遺恨ルール内の名前リストを検証する。"""
    if key not in entry:
        raise SpecLoadError(f"forbidden_co_presence[{rule_index}] missing key: {key}")

    value = entry[key]
    if not isinstance(value, list):
        raise SpecLoadError(f"forbidden_co_presence[{rule_index}].{key} must be a list")

    names: list[str] = []
    for name in value:
        if not isinstance(name, str) or not name:
            raise SpecLoadError(
                f"forbidden_co_presence[{rule_index}].{key} entries must be non-empty strings",
            )
        if name not in item_set:
            raise SpecLoadError(
                f"unknown item in forbidden_co_presence[{rule_index}].{key}: {name!r}",
            )
        names.append(name)

    return names


def _parse_item_weights(
    raw: dict[str, Any],
    items: tuple[str, ...],
) -> dict[str, float]:
    """item_weights を全 items 分パースする。"""
    if "item_weights" not in raw:
        raise SpecLoadError("missing required key: item_weights")

    value = raw["item_weights"]
    if not isinstance(value, dict):
        raise SpecLoadError("item_weights must be a mapping")

    weights: dict[str, float] = {}
    for name in items:
        if name not in value:
            raise SpecLoadError(f"missing weight for item: {name!r}")

    for key, weight in value.items():
        if not isinstance(key, str) or key not in items:
            raise SpecLoadError(f"unknown item in item_weights: {key!r}")
        if not isinstance(weight, (int, float)) or weight < 0:
            raise SpecLoadError(f"weight for {key!r} must be a non-negative number")
        weights[key] = float(weight)

    return weights


def _require_str(raw: dict[str, Any], key: str) -> str:
    """必須の文字列キーを取得する。"""
    if key not in raw:
        raise SpecLoadError(f"missing required key: {key}")
    value = raw[key]
    if not isinstance(value, str) or not value:
        raise SpecLoadError(f"{key} must be a non-empty string")
    return value


def _require_positive_int(raw: dict[str, Any], key: str) -> int:
    """正の整数キーを取得する。"""
    if key not in raw:
        raise SpecLoadError(f"missing required key: {key}")
    value = raw[key]
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise SpecLoadError(f"{key} must be a positive integer")
    return value


def _require_non_negative_int(
    raw: dict[str, Any],
    key: str,
    *,
    default: int,
) -> int:
    """非負整数キーを取得する（省略時は default）。"""
    if key not in raw:
        return default
    value = raw[key]
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise SpecLoadError(f"{key} must be a non-negative integer")
    return value


def _require_positive_float(raw: dict[str, Any], key: str) -> float:
    """正の実数キーを取得する。"""
    if key not in raw:
        raise SpecLoadError(f"missing required key: {key}")
    value = raw[key]
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise SpecLoadError(f"{key} must be a positive number")
    return float(value)


def _require_non_negative_float(
    raw: dict[str, Any],
    key: str,
    *,
    default: float,
) -> float:
    """非負実数キーを取得する（省略時は default）。"""
    if key not in raw:
        return default
    value = raw[key]
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        raise SpecLoadError(f"{key} must be a non-negative number")
    return float(value)
