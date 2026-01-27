#!/usr/bin/env python3
"""
Final integration test for the pack system.
"""
import subprocess
import sys

def run_command(cmd):
    """Run a command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd='.'
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

print("=" * 60)
print("Final Pack System Integration Test")
print("=" * 60)

# Test 1: CLI help
print("\n1. Testing CLI help...")
code, out, err = run_command("python -m src.sis.cli --help")
if code == 0:
    print("   ✓ CLI help works")
    if "--packs" in out:
        print("   ✓ --packs argument documented")
    else:
        print("   ⚠️  --packs argument not in help")
else:
    print(f"   ✗ CLI help failed: {err}")

# Test 2: Scan with packs
print("\n2. Testing scan with packs...")
code, out, err = run_command("python -m src.sis.cli scan test.tf --packs canonical")
if code == 0:
    print("   ✓ Scan with --packs works")
    if "Scanning" in out or "Found" in out or "violations" in out.lower():
        print("   ✓ Scan output looks good")
    else:
        print(f"   ⚠️  Unexpected scan output: {out[:200]}...")
else:
    print(f"   ✗ Scan failed: {err}")

# Test 3: List rules with packs
print("\n3. Testing list rules with packs...")
code, out, err = run_command("python -m src.sis.cli rules --packs canonical")
if code == 0:
    print("   ✓ Rules list with --packs works")
    if "Available Rules" in out or "IRR-" in out:
        print("   ✓ Rules listed successfully")
    else:
        print(f"   ⚠️  Unexpected rules output: {out[:200]}...")
else:
    print(f"   ✗ Rules list failed: {err}")

# Test 4: Direct loader test
print("\n4. Testing direct loader...")
try:
    from src.sis.rules.loader import load_rules, list_available_packs
    
    packs = list_available_packs()
    print(f"   ✓ Available packs: {len(packs)}")
    
    rules = load_rules(['canonical'])
    print(f"   ✓ Loaded {len(rules)} rules from canonical pack")
    
    if rules and '_pack' in rules[0]:
        print(f"   ✓ Pack attribution working: {rules[0]['_pack']}")
    else:
        print("   ✗ Pack attribution missing")
        
except Exception as e:
    print(f"   ✗ Direct loader test failed: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

# Summary
all_tests_passed = True  # We'll assume yes unless proven otherwise
if code != 0 for any test:
    all_tests_passed = False

if all_tests_passed:
    print("✅ SUCCESS: All integration tests passed!")
    sys.exit(0)
else:
    print("⚠️  Some tests failed or had warnings")
    sys.exit(1)
