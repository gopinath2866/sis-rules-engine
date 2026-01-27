import json
from src.sis.rules.loader import load_rules

print("=== Testing Pack Attribution ===")

# Load rules with explicit pack
rules = load_rules(['canonical'])
print(f"Loaded {len(rules)} rules from canonical pack")

# Check a few rules
for i, rule in enumerate(rules[:3]):
    print(f"\nRule {i+1}:")
    print(f"  ID: {rule.get('rule_id', 'N/A')}")
    print(f"  Type: {rule.get('rule_type', 'N/A')}")
    print(f"  Pack: {rule.get('_pack', 'N/A')}")
    print(f"  Pack Version: {rule.get('_pack_version', 'N/A')}")

# Test that all rules have pack attribution
missing_pack = [r for r in rules if '_pack' not in r]
if missing_pack:
    print(f"\n⚠️  Warning: {len(missing_pack)} rules missing _pack attribution")
else:
    print(f"\n✓ All {len(rules)} rules have pack attribution")

# Test loading all available packs (should only be canonical since it's free)
all_rules = load_rules()
print(f"\n=== Loading all available packs ===")
print(f"Loaded {len(all_rules)} total rules")

# Group by pack
from collections import defaultdict
pack_counts = defaultdict(int)
for rule in all_rules:
    pack_counts[rule.get('_pack', 'unknown')] += 1

print("\nRules by pack:")
for pack, count in pack_counts.items():
    print(f"  {pack}: {count} rules")
