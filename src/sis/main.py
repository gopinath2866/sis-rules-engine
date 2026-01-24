"""
Main SIS engine module
"""
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Union, cast
from pathlib import Path

from .parsers import parse_content
from .engine import validate_resources
from .api.schemas import ScanResponse, Finding, Summary, FileError, Severity

# Rate limiting cache
rate_limit_cache: Dict[str, Tuple[float, int]] = {}

def load_rules(rules_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load SIS rules from JSON file, handling both dict and list formats."""
    path_obj: Path
    if rules_path is None:
        path_obj = Path(__file__).parent.parent.parent / "rules" / "canonical.json"
    else:
        path_obj = Path(rules_path)
    
    with open(path_obj, 'r') as f:
        rules_data: Union[Dict[str, Any], List[Dict[str, Any]]] = json.load(f)
    
    # Handle different formats
    if isinstance(rules_data, dict):
        # If it's a dictionary with a 'rules' key
        if 'rules' in rules_data:
            rules_list = cast(List[Dict[str, Any]], rules_data['rules'])
            # Ensure each rule has an 'id' field
            for rule in rules_list:
                if 'rule_id' in rule and 'id' not in rule:
                    rule['id'] = rule['rule_id']
            return rules_list
        # If it's a dictionary of rule_id -> rule
        else:
            # Convert dict of rules to list
            converted_rules_list: List[Dict[str, Any]] = []
            for rule_id, rule in rules_data.items():
                if isinstance(rule, dict):
                    rule['id'] = rule_id  # Ensure id is set
                    converted_rules_list.append(rule)
            return converted_rules_list
    elif isinstance(rules_data, list):
        return rules_data
    else:
        raise ValueError(f"Unexpected rules format: {type(rules_data)}")

def scan_files(
    files: List[Dict[str, Any]],
    client_id: Optional[str] = None,
    rate_limit: bool = True
) -> ScanResponse:
    """Scan files for SIS violations."""
    # Load rules
    rules = load_rules()
    
    all_resources: List[Dict[str, Any]] = []
    all_violations: List[Dict[str, Any]] = []
    all_errors: List[Dict[str, str]] = []
    
    # Process each file
    for file_info in files:
        file_path = file_info.get("path", "unknown")
        content = file_info.get("content", "")
        file_type = file_info.get("type", "")
        file_format = file_info.get("format")
        
        if not content or not file_type:
            all_errors.append({
                "file_path": file_path,
                "error": "Missing content or file type"
            })
            continue
        
        try:
            resources = parse_content(content, file_type, file_format)
            violations = validate_resources(resources, rules)
            
            all_resources.extend(resources)
            all_violations.extend(violations)
                
        except Exception as e:
            all_errors.append({
                "file_path": file_path,
                "error": f"Processing error: {str(e)}"
            })
    
    # Convert violations to Finding objects
    findings: List[Finding] = []
    for violation in all_violations:
        try:
            # Map severity string to Severity enum
            severity_str = violation.get("severity", "medium").lower()
            if severity_str == "critical":
                severity = Severity.CRITICAL
            elif severity_str == "high":
                severity = Severity.HIGH
            elif severity_str == "medium":
                severity = Severity.MEDIUM
            elif severity_str == "low":
                severity = Severity.LOW
            else:
                severity = Severity.INFO
            
            finding = Finding(
                rule_id=violation.get("rule_id", "unknown"),
                resource_id=violation.get("resource_id", "unknown"),
                resource_type=violation.get("resource_type", "unknown"),
                severity=severity,
                message=violation.get("message", ""),
                location=violation.get("location"),
                remediation=violation.get("remediation")
            )
            findings.append(finding)
        except Exception as e:
            # Log error but continue
            print(f"Error creating finding: {e}")
    
    # Create summary
    violations_by_severity: Dict[str, int] = {}
    for violation in all_violations:
        severity = violation.get("severity", "medium")
        violations_by_severity[severity] = violations_by_severity.get(severity, 0) + 1
    
    # Create a list of rule IDs that were evaluated
    rules_evaluated: List[str] = []
    for rule in rules:
        rule_id = rule.get('rule_id') or rule.get('id')
        if rule_id:
            rules_evaluated.append(str(rule_id))
    
    summary = Summary(
        total_resources=len(all_resources),
        total_violations=len(all_violations),
        violations_by_severity=violations_by_severity,
        rules_evaluated=rules_evaluated
    )
    
    # Convert errors to FileError objects
    file_errors: List[FileError] = []
    for error_info in all_errors:
        file_error = FileError(
            file_path=str(error_info.get("file_path", "unknown")),
            error=str(error_info.get("error", "Unknown error"))
        )
        file_errors.append(file_error)
    
    return ScanResponse(
        findings=findings,
        summary=summary,
        errors=file_errors
    )

def cli() -> None:
    """Command-line interface entry point."""
    print("SIS CLI - Not fully implemented")
