"""
SIS Rule Loader

Single authoritative source for loading rules.
All rules MUST come from JSON rule packs.
No Python-defined rules. No alternate loaders.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Rule pack search paths (ordered)
# 1. Project-local packs (development)
# 2. User-installed packs (production)
RULES_BASE_PATHS: List[Path] = [
    Path(__file__).resolve().parents[3] / "rules",
    Path.home() / ".sis" / "rules",
]


class RuleLoadError(Exception):
    """Raised when rule loading fails."""


def load_rules(packs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Load rules from JSON rule packs.

    Args:
        packs: List of pack names to load.
               If None, all discovered packs are loaded.

    Returns:
        Flat list of rule dictionaries.

    Raises:
        RuleLoadError: On malformed packs or invalid rules.
    """
    pack_names = packs if packs is not None else _discover_packs()

    if not pack_names:
        raise RuleLoadError("No rule packs found")

    all_rules: List[Dict[str, Any]] = []

    for pack in pack_names:
        rules = _load_pack(pack)
        all_rules.extend(rules)

    logger.info(
        "Loaded %d rules from packs: %s",
        len(all_rules),
        ", ".join(pack_names),
    )

    return all_rules


def _discover_packs() -> List[str]:
    """Discover all available rule packs."""
    packs = set()

    for base in RULES_BASE_PATHS:
        if not base.exists():
            continue
        for path in base.iterdir():
            if path.is_dir() and (path / "rules.json").is_file():
                packs.add(path.name)

    return sorted(packs)


def _load_pack(pack_name: str) -> List[Dict[str, Any]]:
    """Load a single rule pack."""
    rules_file = _find_pack_rules_file(pack_name)

    try:
        with rules_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise RuleLoadError(f"Invalid JSON in {rules_file}: {e}") from e

    if not isinstance(data, list):
        raise RuleLoadError(
            f"{rules_file} must contain a list of rules"
        )

    rules: List[Dict[str, Any]] = []

    for idx, rule in enumerate(data):
        if not isinstance(rule, dict):
            raise RuleLoadError(
                f"Rule #{idx} in {rules_file} is not an object"
            )

        normalized = _normalize_rule(rule, pack_name, rules_file)
        rules.append(normalized)

    return rules


def _find_pack_rules_file(pack_name: str) -> Path:
    """Locate rules.json for a given pack."""
    for base in RULES_BASE_PATHS:
        candidate = base / pack_name / "rules.json"
        if candidate.is_file():
            return candidate

    raise RuleLoadError(f"Rule pack '{pack_name}' not found")


def _normalize_rule(
    rule: Dict[str, Any],
    pack_name: str,
    source: Path,
) -> Dict[str, Any]:
    """Validate and normalize a rule definition."""
    rule_id = rule.get("id") or rule.get("rule_id")
    if not rule_id or not isinstance(rule_id, str):
        raise RuleLoadError(
            f"Rule in {source} missing valid 'id'"
        )

    normalized = dict(rule)  # shallow copy
    normalized["id"] = rule_id
    normalized["_pack"] = pack_name
    normalized["_source"] = str(source)

    return normalized


def list_available_packs() -> List[str]:
    """Public helper to list available rule packs."""
    return _discover_packs()
