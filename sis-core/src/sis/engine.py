"""
Rule engine for SIS
"""
import re
import json
from typing import Dict, Any, List, Optional

def get_nested_value(obj: Dict[str, Any], path: str) -> Any:
    """
    Get a nested value from a dictionary using dot notation.
    
    Args:
        obj: Dictionary to search
        path: Dot-separated path (e.g., 'lifecycle.prevent_destroy')
    
    Returns:
        The value at the path, or None if not found
    """
    parts = path.split('.')
    current = obj
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    
    return current

def validate_resources(resources: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate resources against rules and return violations.
    
    Args:
        resources: List of resources to validate
        rules: List of rules to check against
    
    Returns:
        List of violations found
    """
    violations = []
    
    for rule in rules:
        rule_id = rule.get('rule_id')
        
        # Check which resources this rule applies to
        if 'applies_to' not in rule:
            continue
            
        resource_kinds = rule['applies_to'].get('resource_kinds', [])
        
        for resource in resources:
            # Check if rule applies to this resource kind
            if resource_kinds and resource_kinds != ['*'] and resource.get('kind') not in resource_kinds:
                continue
            
            # Check detection conditions
            if 'detection' not in rule:
                continue
                
            detection = rule['detection']
            conditions = detection.get('conditions', [])
            match_logic = detection.get('match_logic', 'ALL')
            
            condition_results = []
            
            for condition in conditions:
                path = condition.get('path')
                operator = condition.get('operator')
                value = condition.get('value')
                
                # Get attribute value using nested lookup
                attr_value = get_nested_value(resource.get('attributes', {}), path)
                
                # Apply operator
                if operator == 'REGEX':
                    if attr_value is None:
                        result = False
                    else:
                        result = bool(re.match(str(value), str(attr_value)))
                
                elif operator == 'EQUALS':
                    # Handle boolean string "true" vs Python True
                    if isinstance(attr_value, str) and attr_value.lower() == 'true':
                        attr_value = True
                    elif isinstance(attr_value, str) and attr_value.lower() == 'false':
                        attr_value = False
                    
                    if isinstance(value, str) and value.lower() == 'true':
                        value = True
                    elif isinstance(value, str) and value.lower() == 'false':
                        value = False
                    
                    result = str(attr_value) == str(value)
                
                elif operator == 'EXISTS':
                    # Check if path exists (not None)
                    result = attr_value is not None
                
                elif operator == 'CONTAINS':
                    result = str(value) in str(attr_value) if attr_value else False
                
                elif operator == 'GREATER_THAN':
                    try:
                        result = float(attr_value) > float(value)
                    except:
                        result = False
                
                else:
                    # Unknown operator
                    result = False
                
                condition_results.append(result)
            
            # Apply match logic
            if match_logic == 'ALL':
                rule_matches = all(condition_results)
            elif match_logic == 'ANY':
                rule_matches = any(condition_results)
            else:
                rule_matches = all(condition_results)
            
            if rule_matches:
                # Create violation
                violation = {
                    'rule_id': rule_id,
                    'title': rule.get('title', rule_id),
                    'severity': rule.get('severity', 'MEDIUM'),
                    'message': rule.get('message', ''),
                    'resource_type': resource.get('kind', ''),
                    'resource_name': resource.get('name', ''),
                    'file_path': resource.get('file_path', ''),
                    'line': resource.get('line', 0),
                    'resource_line': resource.get('line', 0)
                }
                violations.append(violation)
    
    return violations
