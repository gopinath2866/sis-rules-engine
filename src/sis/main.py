"""
Main SIS engine module
"""
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from .parsers import parse_content
from .engine import validate_resources
from .api.schemas import ScanResponse, Finding, Summary, FileError

# Rate limiting cache
rate_limit_cache: Dict[str, Tuple[float, int]] = {}

def load_rules(rules_path: Optional[str] = None) -> List[Dict[str, Any]]:
    if rules_path is None:
        rules_path = Path(__file__).parent.parent.parent / "rules" / "canonical.json"
    
    with open(rules_path, 'r') as f:
        return json.load(f)

def scan_files(
    files: List[Dict[str, Any]],
    client_id: Optional[str] = None,
    rate_limit: bool = True
) -> ScanResponse:
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
        finding = Finding(
            rule_id=violation.get("rule_id", "unknown"),
            resource_id=violation.get("resource_id", "unknown"),
            resource_type=violation.get("resource_type", "unknown"),
            severity=violation.get("severity", "medium"),
            message=violation.get("message", ""),
            location=violation.get("location"),
            remediation=violation.get("remediation")
        )
        findings.append(finding)
    
    # Create summary
    violations_by_severity: Dict[str, int] = {}
    for violation in all_violations:
        severity = violation.get("severity", "medium")
        violations_by_severity[severity] = violations_by_severity.get(severity, 0) + 1
    
    summary = Summary(
        total_resources=len(all_resources),
        total_violations=len(all_violations),
        violations_by_severity=violations_by_severity,
        rules_evaluated=[rule.get("id") for rule in rules]
    )
    
    # Convert errors to FileError objects
    file_errors: List[FileError] = []
    for error_info in all_errors:
        file_error = FileError(
            file_path=error_info.get("file_path", "unknown"),
            error=error_info.get("error", "Unknown error")
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
