#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

print("🧪 TESTING NEW TERRAFORM PARSER")
print("=" * 60)

from sis.parsers import parse_content

with open("test_real.tf", "r") as f:
    content = f.read()

resources = parse_content(content, "terraform")
print(f"Parsed {len(resources)} resources\n")

for i, resource in enumerate(resources):
    print(f"Resource {i+1}:")
    print(f"  Kind: {resource.get('kind')}")
    print(f"  Name: {resource.get('name')}")
    print(f"  Line: {resource.get('line')}")
    
    # Show important fields
    for key in ['acl', 'lifecycle', 'policy', 'ingress', 'config']:
        if key in resource:
            print(f"  {key}: {resource[key]}")
    
    print()
