print("=== Simple Pack System Test ===")

# Test 1: Direct loader
try:
    from src.sis.rules.loader import load_rules
    rules = load_rules(['canonical'])
    print(f"✓ Loaded {len(rules)} rules from canonical pack")
    if rules:
        print(f"✓ First rule: {rules[0].get('rule_id', 'N/A')}")
        print(f"✓ Has pack attribution: {'_pack' in rules[0]}")
except Exception as e:
    print(f"✗ Loader failed: {e}")

# Test 2: CLI module import
print("\n=== Testing CLI import ===")
try:
    from src.sis import cli
    print("✓ CLI module imports successfully")
except Exception as e:
    print(f"✗ CLI import failed: {e}")

# Test 3: Test basic functionality
print("\n=== Testing basic functionality ===")
import subprocess
import sys

# Test CLI help
result = subprocess.run([sys.executable, "-m", "src.sis.cli", "--help"], 
                       capture_output=True, text=True)
if result.returncode == 0:
    print("✓ CLI --help works")
    if "--packs" in result.stdout:
        print("✓ --packs argument documented")
else:
    print(f"✗ CLI --help failed: {result.stderr}")

print("\n=== Test Complete ===")
