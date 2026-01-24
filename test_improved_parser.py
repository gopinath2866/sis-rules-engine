#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

print("🧪 TESTING IMPROVED PARSER")
print("=" * 60)

from sis.parsers import parse_content

test_files = [
    "test_clean.tf",
    "test_real.tf", 
    "test_simple.tf"
]

for file in test_files:
    print(f"\n📄 {file}:")
    with open(file, "r") as f:
        content = f.read()
    
    resources = parse_content(content, "terraform")
    print(f"  Parsed {len(resources)} resources")
    
    for r in resources[:3]:  # Show first 3
        print(f"    • {r.get('kind')}.{r.get('name')}")
        if r.get('kind') == 'aws_s3_bucket' and 'acl' in r:
            print(f"      ACL: {r['acl']}")
        if r.get('kind') == 'aws_iam_policy' and 'policy' in r:
            print(f"      Has policy: {type(r['policy'])}")
        if r.get('kind') == 'aws_security_group' and 'ingress' in r:
            print(f"      Has ingress: {type(r['ingress'])}")
