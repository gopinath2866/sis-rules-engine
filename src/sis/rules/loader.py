"""
SIS Rule Loader - Single authoritative source for all rules.
All rules must come from JSON pack files. No Python hardcoded rules.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Explicit base paths in order of priority
# PROJECT FIRST during development, user-installed second
RULES_PATHS = [
    Path(__file__).resolve().parents[3] / "rules",  # Project packs (development)
    Path.home() / ".sis" / "rules",  # User-installed packs (production)
]

def load_rules(pack_names: List[str] = None) -> List[Dict[str, Any]]:
    """
    Load rules from specified packs. If no packs specified, load all available.
    
    Args:
        pack_names: List of pack names to load. If None, loads all packs.
    
    Returns:
        List of rule dictionaries.
    
    Raises:
        ValueError: If a pack is malformed or missing.
        FileNotFoundError: If a requested pack doesn't exist.
    """
    if pack_names is None:
        # Discover all available packs
        pack_names = []
        for base_path in RULES_PATHS:
            if base_path.exists():
                pack_names.extend([p.name for p in base_path.iterdir() if p.is_dir()])
        pack_names = list(set(pack_names))  # Remove duplicates
    
    rules = []
    loaded_packs = []
    
    for pack_name in pack_names:
        try:
            pack_rules = _load_pack(pack_name)
            if pack_rules:
                rules.extend(pack_rules)
                loaded_packs.append(pack_name)
        except (FileNotFoundError, ValueError) as e:
            logger.warning(f"Could not load pack '{pack_name}': {e}")
    
    logger.info(f"Loaded {len(rules)} rules from packs: {', '.join(loaded_packs)}")
    return rules

def _load_pack(pack_name: str) -> List[Dict[str, Any]]:
    """Load a single pack's rules."""
    for base_path in RULES_PATHS:
        rules_file = base_path / pack_name / "rules.json"
        if rules_file.exists():
            try:
                with open(rules_file, 'r') as f:
                    rules_data = json.load(f)
                
                # VALIDATION: Fail loud on malformed packs
                if not isinstance(rules_data, list):
                    raise ValueError(f"Invalid rules format in {rules_file}: must be a list")
                
                # Add pack attribution to each rule
                for rule in rules_data:
                    rule['_pack'] = pack_name
                    # Ensure rule has standard id field
                    if 'rule_id' in rule and 'id' not in rule:
                        rule['id'] = rule['rule_id']
                
                logger.debug(f"Loaded {len(rules_data)} rules from pack '{pack_name}'")
                return rules_data
                
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {rules_file}: {e}")
            except Exception as e:
                raise ValueError(f"Failed to load pack '{pack_name}' from {rules_file}: {e}")
    
    raise FileNotFoundError(f"Pack '{pack_name}' not found in any rule path")

def list_available_packs() -> List[str]:
    """List all available packs across all rule paths."""
    packs = set()
    for base_path in RULES_PATHS:
        if base_path.exists():
            packs.update([p.name for p in base_path.iterdir() if p.is_dir()])
    return sorted(packs)
