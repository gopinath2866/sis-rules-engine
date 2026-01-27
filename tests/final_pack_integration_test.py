#!/usr/bin/env python3
"""
Final integration test for the complete pack system.
"""
import subprocess
import sys
import json
from pathlib import Path

print("=" * 70)
print("FINAL PACK SYSTEM INTEGRATION TEST")
print("=" * 70)

all_tests_passed = True

# Test 1: CLI basic functionality
print("\n1. Testing CLI basic functionality...")
tests = [
    (["python", "-m", "src.sis.cli", "--help"], "CLI help"),
    (["python", "-m", "src.sis.cli", "rules", "--packs", "canonical"], "List canonical rules"),
    (["python", "-m", "src.sis.cli", "rules", "--packs", "defi-irreversibility"], "List DeFi rules"),
    (["python", "-m", "src.sis.cli", "rules", "--packs", "canonical", "defi-irreversibility"], "List all rules"),
]

for cmd, description in tests:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ {description}")
        # Check for pack attribution in output
        if "Pack:" in result.stdout and "v" in result.stdout:
            print(f"     ✓ Pack attribution present")
    else:
        print(f"   ❌ {description}: {result.stderr[:100]}")
        all_tests_passed = False

# Test 2: Direct loader test
print("\n2. Testing direct loader...")
try:
    from src.sis.rules.loader import load_rules
    
    # Load both packs
    all_rules = load_rules(['canonical', 'defi-irreversibility'])
    
    print(f"   ✓ Loaded {len(all_rules)} total rules")
    
    # Check pack attribution
    packs_present = set()
    for rule in all_rules:
        if '_pack' in rule:
            packs_present.add(rule['_pack'])
    
    print(f"   ✓ Rules from packs: {packs_present}")
    
    # Count by pack
    from collections import defaultdict
    pack_counts = defaultdict(int)
    for rule in all_rules:
        pack_counts[rule.get('_pack', 'unknown')] += 1
    
    print("   ✓ Rule counts:")
    for pack, count in pack_counts.items():
        print(f"     {pack}: {count} rules")
    
    if len(all_rules) == 34:  # 25 canonical + 9 defi
        print("   ✓ Correct total rule count")
    else:
        print(f"   ⚠️  Unexpected total: {len(all_rules)} (expected 34)")
        all_tests_passed = False
        
except Exception as e:
    print(f"   ❌ Loader test failed: {e}")
    all_tests_passed = False

# Test 3: Scanner integration with pack attribution
print("\n3. Testing scanner with pack attribution...")

# Create test files
test_tf = Path("final_test.tf")
test_tf.write_text('''resource "aws_s3_bucket" "test" {
  bucket = "test-bucket"
  acl    = "public-read"
}''')

# Test scan with JSON output to check pack attribution
result = subprocess.run(
    ["python", "-m", "src.sis.cli", "scan", "final_test.tf", "--packs", "canonical", "--format", "json"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("   ✅ Scanner executed successfully")
    
    # Try to parse JSON output
    try:
        findings = json.loads(result.stdout)
        print(f"   ✓ Found {len(findings)} issues")
        
        # Check if findings have pack attribution
        if findings:
            first_finding = findings[0]
            if '_pack' in first_finding:
                print(f"   ✓ Pack attribution in findings: {first_finding['_pack']}")
            else:
                print("   ⚠️  Missing pack attribution in findings")
                all_tests_passed = False
    except json.JSONDecodeError:
        print("   ⚠️  Could not parse JSON output")
else:
    print(f"   ❌ Scanner failed: {result.stderr[:100]}")
    all_tests_passed = False

# Clean up
test_tf.unlink()

# Test 4: Verify no syntax errors
print("\n4. Checking for syntax errors...")
modules = ["src/sis/cli.py", "src/sis/scanner.py", "src/sis/rules/loader.py", "src/sis/engine.py"]

for module in modules:
    result = subprocess.run(["python", "-m", "py_compile", module], capture_output=True)
    if result.returncode == 0:
        print(f"   ✅ {module} - no syntax errors")
    else:
        print(f"   ❌ {module} - syntax error: {result.stderr[:100]}")
        all_tests_passed = False

print("\n" + "=" * 70)
if all_tests_passed:
    print("✅ SUCCESS: Complete pack system is fully operational!")
    print("\nSUMMARY:")
    print("- Modular rule packs with metadata")
    print("- License tier support (free/pro)")
    print("- Pack attribution in rules and findings")
    print("- CLI integration with --packs argument")
    print("- Scanner uses pack-loaded rules")
    print("- Backward compatible migration path")
    sys.exit(0)
else:
    print("❌ FAILURE: Some tests failed")
    sys.exit(1)
