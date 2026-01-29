"""
Rule engine for SIS
"""
import re
import json
from typing import Dict, Any, List, Optional

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
            if resource_kinds and resource.get('kind') not in resource_kinds:
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
                
                # Get attribute value
                attr_value = resource.get('attributes', {}).get(path)
                
                # Apply operator
                if operator == 'REGEX':
                    if attr_value is None:
                        result = False
                    else:
                        result = bool(re.match(str(value), str(attr_value)))
                
                elif operator == 'EQUALS':
                    result = str(attr_value) == str(value)
                
                elif operator == 'EXISTS':
                    result = path in resource.get('attributes', {})
                
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

# Legacy function for backward compatibility
def check_resource_rule(resource: Dict[str, Any], rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Legacy function - kept for backward compatibility
    """
    result = validate_resources([resource], [rule])
    return result[0] if result else None
