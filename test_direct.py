#!/usr/bin/env python3
"""
Direct test of the SIS scanner
"""
import sys
sys.path.insert(0, 'src')

from sis.scanner import SISScanner

def test_direct():
    print("🧪 Testing SIS Scanner Directly...")
    
    scanner = SISScanner()
    
    # Test with the vulnerable.tf file
    findings = scanner.scan_file("test_infra/vulnerable.tf")
    
    print(f"\n📊 Found {len(findings)} issues:")
    print("=" * 60)
    
    if not findings:
        print("❌ No issues found! Something is wrong.")
        print("\nDebug info:")
        
        # Let's debug
        from sis.parsers import parse_content
        from sis.engine import validate_resources
        from sis.rules import load_rules
        
        with open("test_infra/vulnerable.tf", "r") as f:
            content = f.read()
        
        print("1. Parsing content...")
        resources = parse_content(content, "terraform")
        print(f"   Parsed {len(resources)} resources")
        
        print("2. Loading rules...")
        rules = load_rules()
        print(f"   Loaded {len(rules)} total rules")
        
        print("3. Validating...")
        violations = validate_resources(resources, rules)
        print(f"   Found {len(violations)} violations")
        
        for i, violation in enumerate(violations):
            print(f"   Violation {i+1}: {violation}")
    else:
        for finding in findings:
            print(f"\n🔸 {finding['rule_id']} [{finding['severity']}]:")
            print(f"   File: {finding['file']}")
            print(f"   Resource: {finding['resource']}")
            print(f"   Issue: {finding['message']}")
            print(f"   Fix: {finding['remediation']}")

if __name__ == "__main__":
    test_direct()
