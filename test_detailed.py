#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

from sis.scanner import SISScanner
import json

print("🔍 DETAILED SCANNER TEST")
print("=" * 60)

scanner = SISScanner()

# Test each file individually with detailed output
test_files = [
    "test_real.tf",
    "test_simple.tf", 
    "test_infra/vulnerable.tf"
]

all_findings = []

for file in test_files:
    print(f"\n📄 Scanning: {file}")
    try:
        findings = scanner.scan_file(file)
        
        if findings:
            print(f"   Found {len(findings)} issues:")
            for f in findings:
                print(f"     • {f['rule_id']}: {f['resource']} - {f['message']}")
                # Add to all findings
                f['file'] = file
                all_findings.append(f)
        else:
            print("   No issues found")
            
    except Exception as e:
        print(f"   Error: {e}")

# Summary
print("\n" + "=" * 60)
print("📊 SUMMARY OF FINDINGS:")

# Group by rule
rules_found = {}
for f in all_findings:
    rule_id = f['rule_id']
    rules_found.setdefault(rule_id, []).append(f)

for rule_id, findings in rules_found.items():
    print(f"\n  {rule_id}: {len(findings)} occurrences")
    for f in findings[:3]:  # Show first 3
        print(f"    - {f['file']}: {f['resource']}")

print("\n" + "=" * 60)

# Check what rules we have
from sis.rules import load_rules
rules = load_rules('terraform')
print(f"📋 Available Terraform rules: {len(rules)}")
for rule in rules:
    print(f"  • {rule['rule_id']}: {rule['message'][:50]}...")

print("\n" + "=" * 60)

# Debug: Check what's in test_real.tf
print("\n🔧 DEBUG: Checking test_real.tf content...")
with open("test_real.tf", "r") as f:
    content = f.read()
    print("\nFile contains:")
    print(content[:500] + "..." if len(content) > 500 else content)
    
# Check parsing
from sis.parsers import parse_content
print("\n🔧 DEBUG: Parsing test_real.tf...")
resources = parse_content(content, "terraform")
for i, resource in enumerate(resources[:3]):  # First 3 resources
    print(f"\nResource {i+1}: {resource.get('kind')}.{resource.get('name')}")
    print(f"  Keys: {list(resource.keys())}")
    if 'acl' in resource:
        print(f"  ACL: {resource['acl']}")
    if 'lifecycle' in resource:
        print(f"  Lifecycle: {resource['lifecycle']}")
