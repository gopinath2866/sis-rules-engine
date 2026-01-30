"""
Rules module for SIS.
Provides functions to load and manage scanning rules.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

def load_rules() -> List[Dict[str, Any]]:
    """
    Load rules from the rules directory.
    
    Returns:
        List of rule dictionaries
    """
    rules = []
    
    # Try to find the rules directory
    # First, look in the project root (../../rules from src/sis/rules)
    rules_dir = Path(__file__).parent.parent.parent.parent / "rules"
    
    if not rules_dir.exists():
        # Fallback to current directory
        rules_dir = Path.cwd() / "rules"
    
    if not rules_dir.exists():
        print(f"⚠️  Rules directory not found: {rules_dir}")
        # Return default rule
        return [{
            'id': 'proxy-admin-not-zero-address',
            'title': 'Proxy admin must not be the zero address',
            'description': 'The admin of a proxy should be a valid address, not 0x0',
            'severity': 'high',
            'gate': 'proxy-upgrade'
        }]
    
    # Try to load rules from canonical directory
    canonical_dir = rules_dir / "canonical"
    if canonical_dir.exists():
        for rule_file in canonical_dir.glob("*.json"):
            try:
                with open(rule_file, 'r') as f:
                    rule_data = json.load(f)
                    if isinstance(rule_data, dict):
                        rules.append(rule_data)
                    elif isinstance(rule_data, list):
                        rules.extend(rule_data)
            except Exception as e:
                print(f"⚠️  Error loading rule from {rule_file.name}: {e}")
    
    # If no rules loaded, return default
    if not rules:
        rules = [{
            'id': 'proxy-admin-not-zero-address',
            'title': 'Proxy admin must not be the zero address',
            'description': 'The admin of a proxy should be a valid address, not 0x0',
            'severity': 'high',
            'gate': 'proxy-upgrade'
        }]
    
    print(f"📚 Loaded {len(rules)} rule(s)")
    return rules
