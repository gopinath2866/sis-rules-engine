#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

# Import directly
from sis.scanner import SISScanner

print("🧪 MANUAL TEST")
scanner = SISScanner()

# Test with our simple file
findings = scanner.scan_file("test_simple.tf")

if findings:
    print(f"\n✅ FOUND {len(findings)} ISSUES:")
    for f in findings:
        print(f"\n  Rule: {f['rule_id']}")
        print(f"  Severity: {f['severity']}")
        print(f"  Message: {f['message']}")
        print(f"  Resource: {f['resource']}")
else:
    print("\n❌ NO ISSUES FOUND")
    print("\nDebugging...")
    
    # Check what's in the file
    with open("test_simple.tf", "r") as f:
        print(f"\nFile content:\n{f.read()}")
