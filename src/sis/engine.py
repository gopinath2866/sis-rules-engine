"""
SIS rules engine for validating infrastructure resources
"""
from typing import Dict, Any, List, Optional, Union
import re

def check_condition(resource: Dict[str, Any], condition: Dict[str, Any]) -> bool:
    """
    Check if a resource matches a condition.
    
    Args:
        resource: The resource to check
        condition: Condition definition with path, operator, value
    
    Returns:
        True if condition matches, False otherwise
    """
    path = condition.get('path', '')
    operator = condition.get('operator', '')
    value = condition.get('value', '')
    
    # Navigate to the value in the resource
    current: Any = resource
    for key in path.split('.'):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return False
    
    # Apply operator
    if operator == 'EXISTS':
        return True
    elif operator == 'EQUALS':
        return str(current) == str(value)
    elif operator == 'NOT_EQUALS':
        return str(current) != str(value)
    elif operator == 'CONTAINS':
        return str(value) in str(current)
    elif operator == 'REGEX':
        try:
            return bool(re.match(str(value), str(current)))
        except re.error:
            return False
    elif operator == 'IN':
        if isinstance(value, list):
            return str(current) in [str(v) for v in value]
        else:
            return False
    else:
        return False

def check_resource_rule(resource: Dict[str, Any], rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Check if a resource violates a specific rule.
    
    Args:
        resource: The resource to check
        rule: Rule definition
    
    Returns:
        Violation dict if rule is violated, None otherwise
    """
    rule_id = rule.get('rule_id', '')
    rule_type = rule.get('rule_type', '')
    
    # Check if rule applies to this resource type
    applies_to = rule.get('applies_to', {})
    resource_kinds = applies_to.get('resource_kinds', [])
    
    resource_type = resource.get('type', '')
    if resource_kinds and resource_type not in resource_kinds:
        return None
    
    # Check detection conditions
    detection = rule.get('detection', {})
    match_logic = detection.get('match_logic', 'ALL')
    conditions = detection.get('conditions', [])
    
    condition_results = []
    for condition in conditions:
        condition_results.append(check_condition(resource, condition))
    
    # Apply match logic
    if match_logic == 'ALL':
        violates = all(condition_results)
    elif match_logic == 'ANY':
        violates = any(condition_results)
    elif match_logic == 'NONE':
        violates = not any(condition_results)
    else:
        violates = False
    
    if violates:
        return {
            'rule_id': rule_id,
            'rule_type': rule_type,
            'resource_id': resource.get('name', 'unknown'),
            'resource_type': resource_type,
            'severity': rule.get('severity', 'medium'),
            'message': rule.get('message', 'Rule violation'),
            'location': resource.get('location', {}),
            'remediation': rule.get('remediation', '')
        }
    
    return None

def validate_resources(resources: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
