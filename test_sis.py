#!/usr/bin/env python3
"""
Test SIS scanner
"""
import os
import tempfile
from src.sis.cli import main
from src.sis.scanner import SISScanner

def test_scanner():
    """Test the scanner with sample files"""
    print("🧪 Testing SIS Scanner...")
    
    # Create test directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create vulnerable Terraform file
        tf_content = '''
resource "aws_s3_bucket" "public_bucket" {
  bucket = "test-public-bucket"
  acl    = "public-read"
}

resource "aws_iam_policy" "admin" {
  name = "test-admin"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "*"
      Resource = "*"
    }]
  })
}
'''
        
        tf_file = os.path.join(tmpdir, "test.tf")
        with open(tf_file, 'w') as f:
            f.write(tf_content)
        
        # Create vulnerable Kubernetes file
        k8s_content = '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-deployment
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: test
        image: nginx
        securityContext:
          privileged: true
          runAsUser: 0
'''
        
        k8s_file = os.path.join(tmpdir, "deployment.yaml")
        with open(k8s_file, 'w') as f:
            f.write(k8s_content)
        
        # Test scanner
        scanner = SISScanner()
        
        print(f"\n🔍 Scanning Terraform file: {tf_file}")
        findings = scanner.scan_file(tf_file)
        print(f"   Found {len(findings)} issues")
        for f in findings:
            print(f"   - {f['rule_id']}: {f['message']}")
        
        print(f"\n🔍 Scanning Kubernetes file: {k8s_file}")
        findings = scanner.scan_file(k8s_file)
        print(f"   Found {len(findings)} issues")
        for f in findings:
            print(f"   - {f['rule_id']}: {f['message']}")
        
        print(f"\n🔍 Scanning directory: {tmpdir}")
        findings = scanner.scan_directory(tmpdir)
        print(f"   Found {len(findings)} total issues")
        
        print("\n✅ All tests passed!")

if __name__ == '__main__':
    test_scanner()
