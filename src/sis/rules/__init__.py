"""Rule definitions for SIS validation engine"""

from typing import Dict, List, Any, Optional

# Import all rule modules
from . import canonical
from . import security

__all__ = ["get_rule", "list_rules", "Rule", "RuleSet", "RULE_SETS"]


class Rule:
    """Base rule class for validation rules"""

    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        category: str,
        severity: str,
        condition: Dict[str, Any],
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.category = category
        self.severity = severity
        self.condition = condition

    def __repr__(self):
        return f"Rule(id={self.rule_id}, name={self.name}, severity={self.severity})"


class RuleSet:
    """Collection of related rules"""

    def __init__(self, name: str, description: str, rules: List[Rule]):
        self.name = name
        self.description = description
        self.rules = rules

    def __len__(self):
        return len(self.rules)

    def __iter__(self):
        return iter(self.rules)


# Combine all rule sets
RULE_SETS = {
    "canonical": RuleSet(
        name="Canonical Rules",
        description="Core validation rules for infrastructure as code",
        rules=canonical.RULES,
    ),
    "security": RuleSet(
        name="Security Rules",
        description="Security-focused validation rules",
        rules=security.RULES,
    ),
}


def get_rule(rule_id: str) -> Optional[Rule]:
    """Get a rule by its ID"""
    for rule_set in RULE_SETS.values():
        for rule in rule_set.rules:
            if rule.rule_id == rule_id:
                return rule
    return None


def list_rules(category: Optional[str] = None) -> List[Rule]:
    """List all rules, optionally filtered by category"""
    rules = []
    for rule_set in RULE_SETS.values():
        for rule in rule_set.rules:
            if category is None or rule.category == category:
                rules.append(rule)
    return rules


# Export commonly used functions
__all__ += ["get_rule", "list_rules", "Rule", "RuleSet", "RULE_SETS"]
