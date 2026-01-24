#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

print("🚀 FINAL COMPREHENSIVE TEST")
print("=" * 60)

from sis.scanner import SISScanner

scanner = SISScanner()

test_files = [
    "test_clean.tf",
    "test_real.tf",
    "test_simple.tf",
    "test_infra/vulnerable.tf"
]

all_findings = []

print("\n📋 EXPECTED FINDINGS:")
print("-" * 40)
print("test_clean.tf should have:")
print("  • TF-001: Public S3 bucket (public-read-write)")
print("  • IRR-DEC-02: Irreversible resource (prevent_destroy)")
print("  • IRR-DEC-01: Admin IAM policy (* actions)")
print("  • TF-002: Open security group (0.0.0.0/0)")
print("  • TF-003: Plaintext secret (database_password)")
print("  • TF-004: Missing encryption")

print("\n🔍 ACTUAL FINDINGS:")
print("-" * 40)

for file in test_files:
    print(f"\n📄 {file}:")
    try:
        findings = scanner.scan_file(file)
        
        if findings:
            print(f"  ✅ Found {len(findings)} issues:")
            for f in findings:
                print(f"    • {f['rule_id']}: {f['resource']}")
                f['file'] = file
                all_findings.append(f)
        else:
            print("  ❌ No issues found")
            
    except Exception as e:
        print(f"  ⚠️  Error: {e}")

# Summary
print("\n" + "=" * 60)
print("📊 FINAL SUMMARY")
print("=" * 60)

# Group by file
by_file = {}
for f in all_findings:
    file = f['file']
    by_file.setdefault(file, []).append(f)

for file, findings in by_file.items():
    print(f"\n{file}: {len(findings)} issues")
    # Group by rule
    rules = {}
    for f in findings:
        rule = f['rule_id']
        rules.setdefault(rule, []).append(f)
    
    for rule, rule_findings in rules.items():
        resources = [f['resource'] for f in rule_findings]
        print(f"  • {rule}: {', '.join(resources)}")

print("\n" + "=" * 60)
print("✅ TEST COMPLETE")

# Check if we found the critical issues
critical_found = any(f['rule_id'] in ['TF-001', 'IRR-DEC-01', 'TF-003'] for f in all_findings)
if critical_found:
    print("\n🎉 CRITICAL ISSUES FOUND! Scanner is working!")
else:
    print("\n⚠️  CRITICAL ISSUES NOT FOUND. Need to debug further.")
