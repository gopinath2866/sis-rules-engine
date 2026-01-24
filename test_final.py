#!/usr/bin/env python3
"""
Final test of SIS scanner
"""
import sys
sys.path.insert(0, 'src')

print("🧪 FINAL TEST OF SIS SCANNER")
print("=" * 60)

# Test 1: Direct parsing
print("\n1. Testing direct parsing...")
from sis.parsers import parse_content

with open("test_simple.tf", "r") as f:
    content = f.read()

resources = parse_content(content, "terraform")
print(f"   Parsed {len(resources)} resources")

for i, resource in enumerate(resources):
    print(f"\n   Resource {i+1}:")
    for key, val in resource.items():
        print(f"     {key}: {repr(val)}")

# Test 2: Engine validation
print("\n2. Testing engine validation...")
from sis.engine import validate_resources
from sis.rules import load_rules

rules = load_rules()
print(f"   Loaded {len(rules)} rules")

violations = validate_resources(resources, rules)
print(f"   Found {len(violations)} violations")

for i, violation in enumerate(violations):
    print(f"\n   Violation {i+1}:")
    for key, val in violation.items():
        print(f"     {key}: {val}")

# Test 3: Full scanner
print("\n3. Testing full scanner...")
from sis.scanner import SISScanner

scanner = SISScanner()
findings = scanner.scan_file("test_simple.tf")
print(f"   Found {len(findings)} findings")

for i, finding in enumerate(findings):
    print(f"\n   Finding {i+1}:")
    print(f"     Rule: {finding.get('rule_id')}")
    print(f"     Severity: {finding.get('severity')}")
    print(f"     Message: {finding.get('message')}")
    print(f"     Resource: {finding.get('resource')}")

print("\n" + "=" * 60)
if findings:
    print("✅ SUCCESS: Scanner found issues!")
else:
    print("❌ FAILURE: Scanner found no issues")
