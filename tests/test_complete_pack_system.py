#!/usr/bin/env python3
"""
Complete test of the pack system with both canonical and DeFi packs.
"""
import json
import sys
from pathlib import Path

print("=" * 70)
print("COMPLETE PACK SYSTEM TEST")
print("=" * 70)

# Test 1: Check both packs exist
print("\n1. Checking available packs...")
from src.sis.rules.loader import list_available_packs

packs = list_available_packs()
expected_packs = {'canonical', 'defi-irreversibility'}
actual_packs = set(packs.keys())

print(f"   Expected packs: {expected_packs}")
print(f"   Actual packs: {actual_packs}")

if expected_packs == actual_packs:
    print("   ✅ All expected packs found")
else:
    print(f"   ❌ Missing packs: {expected_packs - actual_packs}")
    sys.exit(1)

# Test 2: Check metadata
print("\n2. Checking pack metadata...")
for pack_id in ['canonical', 'defi-irreversibility']:
    metadata = packs[pack_id]
    print(f"   {pack_id}:")
    print(f"     Name: {metadata.name}")
    print(f"     Version: {metadata.version}")
    print(f"     License: {metadata.license_required}")
    print(f"     Files: {metadata.rules_files}")

# Test 3: Load rules from each pack
print("\n3. Loading rules from each pack...")

# Canonical (free)
from src.sis.rules.loader import load_rules

canonical_rules = load_rules(['canonical'])
print(f"   Canonical: {len(canonical_rules)} rules loaded")
if canonical_rules:
    print(f"     First rule ID: {canonical_rules[0].get('rule_id', 'N/A')}")
    print(f"     Has _pack: {'_pack' in canonical_rules[0]}")

# DeFi (pro - should work with simple license manager)
defi_rules = load_rules(['defi-irreversibility'])
print(f"   DeFi Irreversibility: {len(defi_rules)} rules loaded")
if defi_rules:
    print(f"     First rule keys: {list(defi_rules[0].keys())[:5]}")
    print(f"     Has _pack: {'_pack' in defi_rules[0]}")

# Test 4: Load both packs together
print("\n4. Loading both packs together...")
all_rules = load_rules(['canonical', 'defi-irreversibility'])
print(f"   Total rules: {len(all_rules)}")

# Group by pack
from collections import defaultdict
pack_counts = defaultdict(int)
for rule in all_rules:
    pack_counts[rule.get('_pack', 'unknown')] += 1

print("   Rules by pack:")
for pack, count in pack_counts.items():
    print(f"     {pack}: {count} rules")

# Test 5: CLI integration
print("\n5. Testing CLI integration...")
import subprocess

# Test rules command
cmds = [
    ['python', '-m', 'src.sis.cli', 'rules', '--packs', 'canonical'],
    ['python', '-m', 'src.sis.cli', 'rules', '--packs', 'defi-irreversibility'],
]

for cmd in cmds:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ {' '.join(cmd)}")
    else:
        print(f"   ❌ {' '.join(cmd)}: {result.stderr[:100]}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)

if len(all_rules) > 25:  # Should have more than just canonical
    print("✅ SUCCESS: Pack system is fully functional!")
    print(f"   Total rules across all packs: {len(all_rules)}")
    print(f"   Packs loaded: {list(pack_counts.keys())}")
else:
    print("⚠️  WARNING: May not be loading DeFi rules correctly")
    print(f"   Total rules: {len(all_rules)} (expected > 25)")

sys.exit(0 if len(all_rules) > 25 else 1)
