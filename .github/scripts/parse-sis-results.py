#!/usr/bin/env python3
import json
import os
import sys

REPORT_FILE = 'sis-proxy-upgrade-report.json'

def main():
    if not os.path.exists(REPORT_FILE):
        print(f"::error::SIS report not found: {REPORT_FILE}")
        sys.exit(1)
    
    try:
        with open(REPORT_FILE, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"::error::Failed to parse SIS report: {e}")
        sys.exit(1)
    
    violations = data.get('violations', [])
    total_violations = data.get('total_violations', 0)
    
    print(f"## 📋 SIS Proxy Upgrade Gate Report")
    print(f"**Scanned paths:** {', '.join(data.get('scan_paths', []))}")
    print(f"**Total violations:** {total_violations}")
    print()
    
    if not violations:
        print("✅ **All checks passed!** No violations found.")
        return 0
    
    blocking = [v for v in violations if v.get('severity') in ['HARD_FAIL', 'POLICY_REQUIRED']]
    
    for v in violations:
        level = 'error' if v.get('severity') in ['HARD_FAIL', 'POLICY_REQUIRED'] else 'warning'
        file_path = v.get('file_path', 'unknown')
        line = v.get('line', 1)
        rule_id = v.get('rule_id', 'Unknown')
        message = v.get('message', 'No message')
        print(f"::{level} file={file_path},line={line}::{rule_id}: {message}")
    
    if blocking:
        print(f"\n::error::Found {len(blocking)} blocking violation(s) - PR cannot be merged")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
