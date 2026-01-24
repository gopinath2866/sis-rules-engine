import json
from pathlib import Path

# Test 1: Can we load rules?
rules_path = Path("rules/canonical.json")
with open(rules_path, 'r') as f:
    rules_data = json.load(f)
    
print(f"✓ Loaded rules from {rules_path}")

# Check if it's a dict or list
if isinstance(rules_data, dict):
    print(f"  Structure: Dictionary with {len(rules_data)} keys")
    print(f"  Keys: {list(rules_data.keys())}")
    
    # Check if there's a 'rules' key
    if 'rules' in rules_data:
        rules_list = rules_data['rules']
        print(f"  Found 'rules' key with {len(rules_list)} rules")
        for rule in rules_list[:3]:  # Just first 3
            print(f"    - {rule.get('id', 'no-id')}: {rule.get('name', 'no-name')}")
    else:
        # Maybe it's a dictionary of rules
        print("  No 'rules' key found. Assuming dictionary of rules...")
        for i, (rule_id, rule) in enumerate(list(rules_data.items())[:3]):
            print(f"    - {rule_id}: {rule.get('name', 'no-name')}")
        
elif isinstance(rules_data, list):
    print(f"  Structure: List with {len(rules_data)} rules")
    for rule in rules_data[:3]:  # Just first 3
        print(f"    - {rule.get('id', 'no-id')}: {rule.get('name', 'no-name')}")
else:
    print(f"  Unknown structure: {type(rules_data)}")

print("\n✅ Basic functionality works!")
