#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

from sis.parsers import parse_content
from sis.engine import validate_resources
from sis.rules import load_rules

print("🔍 DEBUGGING SCANNER...")

# Read test file
with open("test_infra/vulnerable.tf", "r") as f:
    content = f.read()

print("\n1. CONTENT BEING PARSED:")
print(content[:500] + "..." if len(content) > 500 else content)

print("\n2. PARSING AS TERRAFORM...")
resources = parse_content(content, "terraform")
print(f"   Parsed {len(resources)} resources")
for i, resource in enumerate(resources):
    print(f"\n   Resource {i+1}:")
    for key, value in resource.items():
        print(f"     {key}: {value}")

print("\n3. LOADING RULES...")
rules = load_rules()
print(f"   Loaded {len(rules)} rules")
for i, rule in enumerate(rules[:5]):  # Show first 5 rules
    print(f"\n   Rule {i+1} (ID: {rule.get('rule_id', rule.get('id', 'unknown'))}):")
    print(f"     Type: {rule.get('rule_type')}")
    print(f"     Applies to: {rule.get('applies_to', {}).get('resource_kinds', [])}")
    print(f"     Detection: {rule.get('detection', {}).get('conditions', [])}")

print("\n4. VALIDATING RESOURCES...")
violations = validate_resources(resources, rules)
print(f"   Found {len(violations)} violations")
for i, violation in enumerate(violations):
    print(f"\n   Violation {i+1}:")
    for key, value in violation.items():
        print(f"     {key}: {value}")

print("\n5. CHECKING SPECIFIC RESOURCE TYPES...")
# Check if we have S3 bucket resources
s3_resources = [r for r in resources if r.get('type') == 'aws_s3_bucket' or r.get('kind') == 'aws_s3_bucket']
print(f"   Found {len(s3_resources)} S3 bucket resources")

# Check if we have IAM policy resources  
iam_resources = [r for r in resources if 'iam_policy' in str(r.get('type', '')).lower() or 'iam_policy' in str(r.get('kind', '')).lower()]
print(f"   Found {len(iam_resources)} IAM policy resources")

print("\n6. CHECKING RULE CONDITIONS...")
# Check TF-002 rule specifically
tf002_rule = None
for rule in rules:
    rule_id = rule.get('rule_id') or rule.get('id', '')
    if 'TF-002' in str(rule_id) or 'TF002' in str(rule_id):
        tf002_rule = rule
        break

if tf002_rule:
    print(f"   Found TF-002 rule: {tf002_rule}")
    # Check what conditions it expects
    conditions = tf002_rule.get('detection', {}).get('conditions', [])
    print(f"   Rule conditions: {conditions}")
    
    # Check if any resource matches these conditions
    for resource in resources:
        resource_type = resource.get('type') or resource.get('kind', '')
        if 's3_bucket' in str(resource_type).lower():
            print(f"\n   Checking S3 bucket resource: {resource}")
            acl_value = resource.get('acl') or resource.get('config', {}).get('acl')
            print(f"   ACL value: {acl_value}")
