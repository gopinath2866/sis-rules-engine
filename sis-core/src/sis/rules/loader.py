"""
SIS rule pack loader
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any

def load_packs(pack_names: List[str]) -> List[Dict[str, Any]]:
    """Load rules from specified packs"""
    all_rules = []
    
    for pack_name in pack_names:
        pack_path = Path(__file__).parent.parent.parent.parent / "rules" / pack_name
        rules_file = pack_path / "rules.json"
        
        if rules_file.exists():
            try:
                with open(rules_file, 'r') as f:
                    rules_data = json.load(f)
                    if isinstance(rules_data, list):
                        all_rules.extend(rules_data)
                    else:
                        all_rules.append(rules_data)
            except Exception as e:
                print(f"⚠️  Error loading pack {pack_name}: {e}")
        else:
            print(f"⚠️  Pack not found: {pack_name}")
    
    return all_rules

# Alias for backward compatibility
load_rules = load_packs
