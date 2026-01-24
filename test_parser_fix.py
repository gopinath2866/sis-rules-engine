#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

from sis.parsers import parse_content

print("🧪 TESTING PARSER FIXES")
print("=" * 60)

with open("test_real.tf", "r") as f:
    content = f.read()

resources = parse_content(content, "terraform")

print(f"Parsed {len(resources)} resources\n")

for r in resources:
    if r.get('kind') == 'aws_s3_bucket':
        print(f"S3 Bucket: {r.get('name')}")
        print(f"  ACL value: {repr(r.get('acl'))}")
        print(f"  ACL type: {type(r.get('acl'))}")
        print(f"  Lifecycle: {r.get('lifecycle')}")
        print()
    
    if r.get('kind') == 'aws_iam_policy':
        print(f"IAM Policy: {r.get('name')}")
        print(f"  Policy value: {repr(r.get('policy'))[:100]}...")
        print()
    
    if r.get('kind') == 'aws_security_group':
        print(f"Security Group: {r.get('name')}")
        print(f"  Ingress: {r.get('ingress')}")
        print()
