#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

print("🧪 COMPREHENSIVE SIS TEST")
print("=" * 60)

from sis.scanner import SISScanner

scanner = SISScanner()

# Test 1: Real Terraform file
print("\n1. Testing test_real.tf:")
findings = scanner.scan_file("test_real.tf")

if findings:
    print(f"✅ Found {len(findings)} issues:")
    for f in findings:
        print(f"\n  Rule: {f['rule_id']} [{f['severity']}]")
        print(f"  Resource: {f['resource']}")
        print(f"  Message: {f['message']}")
        print(f"  File: {f['file']}:{f.get('line', '?')}")
else:
    print("❌ No issues found")

# Test 2: Simple Terraform file
print("\n2. Testing test_simple.tf:")
findings = scanner.scan_file("test_simple.tf")

if findings:
    print(f"✅ Found {len(findings)} issues:")
    for f in findings:
        print(f"  - {f['rule_id']}: {f['message']}")
else:
    print("❌ No issues found")

# Test 3: Directory scan
print("\n3. Testing directory scan:")
findings = scanner.scan_directory(".")

if findings:
    print(f"✅ Found {len(findings)} total issues in directory")
    # Group by file
    by_file = {}
    for f in findings:
        file = f['file']
        by_file.setdefault(file, []).append(f)
    
    for file, file_findings in by_file.items():
        print(f"\n  {file}: {len(file_findings)} issues")
        for f in file_findings[:3]:  # Show first 3
            print(f"    - {f['rule_id']}: {f['resource']}")
else:
    print("❌ No issues found in directory")

print("\n" + "=" * 60)
print("✅ TESTS COMPLETE")
