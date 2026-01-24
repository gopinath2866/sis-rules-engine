#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

from sis.parsers import parse_content

with open("test_real.tf", "r") as f:
    content = f.read()

resources = parse_content(content, "terraform")

print("Checking S3 bucket resources for ACL:")
for r in resources:
    if r.get('kind') == 'aws_s3_bucket':
        print(f"\nS3 Bucket: {r.get('name')}")
        print(f"  Full resource: {r}")
        print(f"  ACL key exists: {'acl' in r}")
        print(f"  ACL value: {r.get('acl')}")
        print(f"  Config: {r.get('config')}")
        
        # Check config for ACL
        config = r.get('config', {})
        if isinstance(config, dict):
            print(f"  Config keys: {list(config.keys())}")
            if 'acl' in config:
                print(f"  ACL in config: {config['acl']}")
