#!/usr/bin/env python3
"""
Final verification of the complete pack system.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

print("=" * 70)
print("FINAL PACK SYSTEM VERIFICATION")
print("=" * 70)

all_tests_passed = True

# Test 1: Check pack structure
print("\n1. Verifying pack structure...")
pack_dir = Path.home() / '.sis' / 'rules' / 'canonical'
metadata_file = pack_dir / 'metadata.json'
rules_file = pack_dir / 'rules.json'

if pack_dir.exists():
    print(f"   ✓ Pack directory exists: {pack_dir}")
else:
    print(f"   ✗ Pack directory missing: {pack_dir}")
    all_tests_passed = False

if metadata_file.exists():
    print(f"   ✓ Metadata file exists: {metadata_file}")
    with open(metadata_file) as f:
        metadata = json.load(f)
    print(f"   ✓ Pack ID: {metadata.get('pack_id', 'N/A')}")
    print(f"   ✓ Version: {metadata.get('version', 'N/A')}")
    print(f"   ✓ License: {metadata.get('license_required', 'N/A')}")
else:
    print(f"   ✗ Metadata file missing")
    all_tests_passed = False

if rules_file.exists():
    print(f"   ✓ Rules file exists: {rules_file}")
    with open(rules_file) as f:
        rules_data = json.load(f)
    if isinstance(rules_data, dict) and 'rules' in rules_data:
        print(f"   ✓ Contains {len(rules_data['rules'])} rules")
    else:
        print(f"   ✗ Invalid rules structure")
        all_tests_passed = False
else:
    print(f"   ✗ Rules file missing")
    all_tests_passed = False

# Test 2: Direct loader test
print("\n2. Testing direct loader...")
try:
    from src.sis.rules.loader import load_rules, list_available_packs
    
    packs = list_available_packs()
    if 'canonical' in packs:
        print(f"   ✓ Found canonical pack in discovery")
        metadata = packs['canonical']
        print(f"   ✓ Metadata accessible: {metadata.name}")
    else:
        print(f"   ✗ Canonical pack not found in discovery")
        all_tests_passed = False
    
    rules = load_rules(['canonical'])
    if len(rules) == 25:
        print(f"   ✓ Loaded {len(rules)} rules (correct count)")
    else:
        print(f"   ✗ Expected 25 rules, got {len(rules)}")
        all_tests_passed = False
    
    if rules and '_pack' in rules[0]:
        print(f"   ✓ Pack attribution present: {rules[0]['_pack']}")
    else:
        print(f"   ✗ Missing pack attribution")
        all_tests_passed = False
        
except Exception as e:
    print(f"   ✗ Direct loader test failed: {e}")
    all_tests_passed = False

# Test 3: CLI functionality
print("\n3. Testing CLI functionality...")
test_cmds = [
    ["python", "-m", "src.sis.cli", "--help"],
    ["python", "-m", "src.sis.cli", "rules", "--packs", "canonical"],
]

for cmd in test_cmds:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✓ {' '.join(cmd)} - success")
    else:
        print(f"   ✗ {' '.join(cmd)} - failed: {result.stderr[:100]}")
        all_tests_passed = False

# Test 4: Scanner integration
print("\n4. Testing scanner integration...")
try:
    from src.sis.scanner import SISScanner
    
    # Create test file
    test_content = '''resource "aws_s3_bucket" "test" {
  bucket = "my-test-bucket"
}'''
    
    test_file = Path("verify_test.tf")
    test_file.write_text(test_content)
    
    scanner = SISScanner()
    results = scanner.scan_file(str(test_file))
    
    print(f"   ✓ Scanner executed successfully")
    print(f"   ✓ Found {len(results)} issues")
    
    # Clean up
    test_file.unlink()
    
except Exception as e:
    print(f"   ✗ Scanner test failed: {e}")
    all_tests_passed = False

# Test 5: Migration readiness
print("\n5. Checking migration readiness...")
old_rules = Path("rules/canonical.json")
if old_rules.exists():
    print(f"   ⚠️  Legacy rules file exists (can be migrated)")
    print(f"   Run: mkdir -p ~/.sis/rules/canonical && cp rules/canonical.json ~/.sis/rules/canonical/rules.json")
else:
    print(f"   ✓ No legacy rules to migrate")

print("\n" + "=" * 70)
if all_tests_passed:
    print("✅ SUCCESS: Pack system is fully operational!")
    print("\nNEXT STEPS:")
    print("1. Create more packs (defi-irreversibility, compliance, etc.)")
    print("2. Implement license validation for pro/enterprise packs")
    print("3. Add 'sis packs' subcommand for pack management")
    print("4. Create pack registry for distribution")
    sys.exit(0)
else:
    print("⚠️  Some tests failed - check above for details")
    sys.exit(1)
