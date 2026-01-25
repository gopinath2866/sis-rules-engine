"""
SIS rules engine for validating infrastructure resources
"""

import re
from typing import Any, Dict, List, Optional, Union, cast


def check_condition(resource: Dict[str, Any], condition: Dict[str, Any]) -> bool:
    """
    Check if a resource matches a condition.

    Args:
        resource: The resource to check
        condition: Condition definition with path, operator, value

    Returns:
        True if condition matches, False otherwise
    """
    path = condition.get("path", "")
    operator = condition.get("operator", "")
    value = condition.get("value", "")

    # Navigate to the value in the resource
    current: Any = resource
    keys = path.split(".")

    for key in keys:
        if key.endswith("[]"):
            # Array access
            array_key = key[:-2]
            if isinstance(current, dict) and array_key in current:
                current = current[array_key]
                if isinstance(current, list) and current:
                    current = current[0]  # Take first element for checking
                else:
                    return False
            else:
                return False
        else:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                # Path doesn't exist
                if operator == "NOT_EXISTS":
                    return True
                return False

    # Convert current to string for comparison
    current_str = str(current).lower() if current is not None else ""
    value_str = str(value).lower()

    # Apply operator
    if operator == "EXISTS":
        return True
    elif operator == "NOT_EXISTS":
        return False  # If we got here, path exists, so NOT_EXISTS is False
    elif operator == "EQUALS":
        # Case-insensitive comparison for string values
        return current_str == value_str
    elif operator == "NOT_EQUALS":
        return current_str != value_str
    elif operator == "CONTAINS":
        return value_str in current_str
    elif operator == "REGEX":
        try:
            return bool(re.search(value_str, current_str, re.IGNORECASE))
        except re.error:
            return False
    elif operator == "IN":
        if isinstance(value, list):
            value_list = [str(v).lower() for v in value]
            return current_str in value_list
        else:
            return False
    else:
        return False


def check_resource_rule(
    resource: Dict[str, Any], rule: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Check if a resource violates a specific rule.

    Args:
        resource: The resource to check
        rule: Rule definition

    Returns:
        Violation dict if rule is violated, None otherwise
    """
    rule_id = rule.get("rule_id", "")
    rule_type = rule.get("rule_type", "")

    # Check if rule applies to this resource type
    applies_to = rule.get("applies_to", {})
    resource_kinds = applies_to.get("resource_kinds", [])

    resource_type = resource.get("type") or resource.get("kind", "")
    if (
        resource_kinds
        and resource_kinds != ["*"]
        and resource_type not in resource_kinds
    ):
        return None

    # Check detection conditions
    detection = rule.get("detection", {})
    match_logic = detection.get("match_logic", "ALL")
    conditions = detection.get("conditions", [])

    condition_results = []
    for condition in conditions:
        condition_results.append(check_condition(resource, condition))

    # Apply match logic
    if match_logic == "ALL":
        violates = all(condition_results)
    elif match_logic == "ANY":
        violates = any(condition_results)
    elif match_logic == "NONE":
        violates = not any(condition_results)
    else:
        violates = False

    if violates:
        return {
            "rule_id": rule_id,
            "rule_type": rule_type,
            "resource_id": resource.get("name", "unknown"),
            "resource_type": resource_type,
            "severity": rule.get("severity", "medium").upper(),
            "message": rule.get("message", "Rule violation"),
            "location": {"line": resource.get("line", 0)},
            "remediation": rule.get("remediation", ""),
        }

    return None


def validate_resources(
    resources: List[Dict[str, Any]], rules: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Validate resources against SIS rules.

    Args:
        resources: List of resources to validate
        rules: List of rules to check

    Returns:
        List of violations found
    """
    violations: List[Dict[str, Any]] = []

    for resource in resources:
        for rule in rules:
            violation = check_resource_rule(resource, rule)
            if violation:
                violations.append(violation)

    return violations
