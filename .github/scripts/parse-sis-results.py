#!/usr/bin/env python3
"""
Parse SIS JSON report and output GitHub annotations.
"""
import json
import os
import sys

REPORT_FILE = 'sis-proxy-upgrade-report.json'

def main():
    # Check if report exists
    if not os.path.exists(REPORT_FILE):
        print(f"::error::SIS report not found: {REPORT_FILE}")
        sys.exit(1)
    
    # Load and parse report
    try:
        with open(REPORT_FILE, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"::error::Failed to parse SIS report: {e}")
        sys.exit(1)
    
    violations = data.get('violations', [])
    total_violations = data.get('total_violations', 0)
    
    # Summary
    print(f"## 📋 SIS Proxy Upgrade Gate Report")
    print(f"**Scanned paths:** {', '.join(data.get('scan_paths', []))}")
    print(f"**Total violations:** {total_violations}")
    print()
    
    if not violations:
        print("✅ **All checks passed!** No violations found.")
        return 0
    
    # Group violations by severity
    by_severity = {}
    for v in violations:
        severity = v.get('severity', 'UNKNOWN')
        by_severity.setdefault(severity, []).append(v)
    
    # Output annotations for each violation
    for severity, violations_list in by_severity.items():
        count = len(violations_list)
        print(f"### {severity} ({count})")
        print()
        
        for i, v in enumerate(violations_list, 1):
            # Determine GitHub annotation level
            if severity in ['HARD_FAIL', 'POLICY_REQUIRED']:
                gh_level = 'error'
                icon = '❌'
            elif severity == 'WARN':
                gh_level = 'warning'
                icon = '⚠️'
            else:
                gh_level = 'notice'
                icon = 'ℹ️'
            
            # GitHub annotation format
            file_path = v.get('file_path', 'unknown')
            line = v.get('line', 1)
            rule_id = v.get('rule_id', 'Unknown')
            message = v.get('message', 'No message')
            
            print(f"{icon} **{rule_id}** - {message}")
            print(f"   - File: `{file_path}:{line}`")
            print(f"   - Resource: {v.get('resource_type', 'unknown')}.{v.get('resource_name', 'unknown')}")
            print()
            
            # Output GitHub annotation
            annotation_msg = f"{rule_id}: {message}"
            print(f"::{gh_level} file={file_path},line={line}::{annotation_msg}")
    
    # Check for blocking violations
    blocking = [v for v in violations if v.get('severity') in ['HARD_FAIL', 'POLICY_REQUIRED']]
    if blocking:
        print(f"\n::error::Found {len(blocking)} blocking violation(s) - PR cannot be merged")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
