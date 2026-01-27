"""
Rule pack loader with license validation and pack isolation.
"""
import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from ..license_simple import (
    validate_license_tier, 
    get_license_manager,
    LicenseError
)

logger = logging.getLogger(__name__)


@dataclass
class PackMetadata:
    """Validated pack metadata."""
    pack_id: str
    version: str
    name: str
    description: str
    license_required: str  # "free" | "pro" | "enterprise"
    engine_compatibility: Dict[str, str]
    rules_files: List[str]
    tags: List[str]
    
    @classmethod
    def from_dict(cls, data: Dict) -> Optional['PackMetadata']:
        """Create from dict with validation."""
        try:
            return cls(
                pack_id=data['pack_id'],
                version=data['version'],
                name=data.get('name', data['pack_id']),
                description=data.get('description', ''),
                license_required=data.get('license_required', 'free'),
                engine_compatibility=data.get('engine_compatibility', {
                    'min': '1.0.0',
                    'max': '2.x'
                }),
                rules_files=data.get('rules_files', []),
                tags=data.get('tags', [])
            )
        except KeyError:
            return None


class PackLoader:
    """Load and validate rule packs."""
    
    def __init__(self):
        self.pack_dirs = self._find_pack_directories()
        self.loaded_packs: Dict[str, PackMetadata] = {}
        self.license_manager = get_license_manager()
        self._discovery_cache: Optional[Dict[str, PackMetadata]] = None
        self._cache_timestamp = 0.0
    
    def _find_pack_directories(self) -> List[Path]:
        """Return ordered list of rule directories (priority order)."""
        dirs = []
        
        # 1. Environment override (highest priority)
        env_dir = os.environ.get('SIS_RULES_DIR')
        if env_dir:
            env_path = Path(env_dir).expanduser().resolve()
            if env_path.exists():
                logger.debug(f"Using rules dir from env: {env_path}")
                dirs.append(env_path)
        
        # 2. User directory
        user_dir = Path.home() / '.sis' / 'rules'
        if user_dir.exists():
            logger.debug(f"Using user rules dir: {user_dir}")
            dirs.append(user_dir)
        
        # 3. Built-in directory (fallback)
        builtin_dir = Path(__file__).resolve().parents[3] / 'rules'
        if builtin_dir.exists():
            logger.debug(f"Using built-in rules dir: {builtin_dir}")
            dirs.append(builtin_dir)
        
        # Log the order for debugging
        logger.debug(f"Rule directory search order: {dirs}")
        return dirs
    
    def _compute_cache_timestamp(self) -> float:
        """Compute latest mtime across all pack directories."""
        latest = 0.0
        for pack_dir in self.pack_dirs:
            if not pack_dir.exists():
                continue
            try:
                # Check directory itself
                latest = max(latest, pack_dir.stat().st_mtime)
                # Check all files in the directory
                for path in pack_dir.rglob('*'):
                    if path.is_file():
                        latest = max(latest, path.stat().st_mtime)
            except OSError:
                pass
        return latest
    
    def _is_cache_stale(self) -> bool:
        """Check if the discovery cache is stale."""
        if self._discovery_cache is None:
            return True
        
        current_timestamp = self._compute_cache_timestamp()
        return current_timestamp > self._cache_timestamp
    
    def _parse_version(self, version_str: str) -> Tuple[int, int, int]:
        """Parse version string into major, minor, patch tuple."""
        # Remove any pre-release suffixes
        version_str = version_str.split('-')[0].split('+')[0]
        parts = version_str.split('.')
        
        # Ensure we have at least 3 parts
        while len(parts) < 3:
            parts.append('0')
        
        try:
            return tuple(int(p) for p in parts[:3])
        except ValueError:
            return (0, 0, 0)
    
    def _validate_pack_compatibility(self, metadata: PackMetadata) -> bool:
        """Check pack compatibility with current engine using simple version comparison."""
        from .. import __version__
        current_version = __version__
        
        min_version = metadata.engine_compatibility.get('min', '0.0.0')
        max_version = metadata.engine_compatibility.get('max', '999.999.999')
        
        # Parse versions
        current = self._parse_version(current_version)
        min_v = self._parse_version(min_version)
        
        # Handle max version (simple check for major version wildcard)
        if max_version.endswith('.x'):
            # For "2.x", check that major version matches
            base = max_version[:-2]
            max_major = self._parse_version(base)[0]
            return min_v <= current and current[0] == max_major
        else:
            max_v = self._parse_version(max_version)
            return min_v <= current <= max_v
    
    def discover_packs(self) -> Dict[str, PackMetadata]:
        """Discover all available packs in pack directories."""
        # Check cache
        if not self._is_cache_stale() and self._discovery_cache is not None:
            return self._discovery_cache.copy()
        
        packs = {}
        
        for pack_dir in self.pack_dirs:
            if not pack_dir.exists():
                continue
            
            for item in pack_dir.iterdir():
                if not item.is_dir():
                    continue
                
                metadata_file = item / 'metadata.json'
                if not metadata_file.exists():
                    continue
                
                try:
                    with open(metadata_file, 'r') as f:
                        metadata_dict = json.load(f)
                    
                    metadata = PackMetadata.from_dict(metadata_dict)
                    if not metadata:
                        logger.warning(f"Invalid metadata in {metadata_file}")
                        continue
                    
                    # Skip if we already have this pack (respect priority)
                    if metadata.pack_id in packs:
                        logger.debug(f"Skipping duplicate pack {metadata.pack_id} from {item}")
                        continue
                    
                    # Validate compatibility
                    if not self._validate_pack_compatibility(metadata):
                        logger.warning(
                            f"Pack '{metadata.pack_id}' requires engine "
                            f"version {metadata.engine_compatibility['min']}-"
                            f"{metadata.engine_compatibility['max']}"
                        )
                        continue
                    
                    packs[metadata.pack_id] = metadata
                    
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Failed to load metadata from {metadata_file}: {e}")
        
        # Update cache
        self._discovery_cache = packs
        self._cache_timestamp = self._compute_cache_timestamp()
        
        logger.info(f"Discovered {len(packs)} packs: {list(packs.keys())}")
        return packs
    
    def load_pack_rules(self, pack_id: str) -> List[Dict[str, Any]]:
        """Load all rules from a specific pack."""
        if pack_id not in self.loaded_packs:
            # Try to discover it
            packs = self.discover_packs()
            if pack_id not in packs:
                raise ValueError(f"Pack '{pack_id}' not found")
            self.loaded_packs[pack_id] = packs[pack_id]
        
        metadata = self.loaded_packs[pack_id]
        
        # License check - TWO LEVELS
        # 1. Check tier
        if metadata.license_required != 'free':
            if not validate_license_tier(metadata.license_required):
                raise LicenseError(
                    f"License tier '{metadata.license_required}' required for pack '{pack_id}'"
                )
            # 2. For non-free packs, check pack-specific allowance
            if not self.license_manager.allows_pack(pack_id):
                raise LicenseError(
                    f"License does not allow access to pack '{pack_id}'"
                )
        
        rules = []
        pack_dir = self._find_pack_directory(pack_id)
        
        for rule_file in metadata.rules_files:
            file_path = pack_dir / rule_file
            if not file_path.exists():
                logger.warning(f"Rule file {rule_file} not found in pack {pack_id}")
                continue
            
            try:
                with open(file_path, 'r') as f:
                    content = json.load(f)
                
                # Handle different JSON structures
                if isinstance(content, list):
                    # It's already a list of rules
                    rule_list = content
                elif isinstance(content, dict):
                    # Check if it has a "rules" key
                    if "rules" in content and isinstance(content["rules"], list):
                        rule_list = content["rules"]
                    else:
                        # Treat the entire dict as a single rule
                        rule_list = [content]
                else:
                    logger.warning(f"Invalid rule format in {file_path}")
                    continue
                
                # Ensure each rule has pack attribution (safe copy)
                for rule in rule_list:
                    rule_copy = dict(rule)
                    rule_copy['_pack'] = pack_id
                    rule_copy['_pack_version'] = metadata.version
                    rules.append(rule_copy)
                    
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading {rule_file} from pack {pack_id}: {e}")
        
        logger.debug(f"Loaded {len(rules)} rules from pack '{pack_id}'")
        return rules
    
    def _find_pack_directory(self, pack_id: str) -> Path:
        """Find the directory containing a specific pack."""
        for pack_dir in self.pack_dirs:
            candidate = pack_dir / pack_id
            if candidate.exists() and (candidate / 'metadata.json').exists():
                return candidate
        raise ValueError(f"Pack directory for '{pack_id}' not found")
    
    def load_rules(
        self,
        enabled_packs: Optional[List[str]] = None,
        skip_license_check: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Load rules from specified packs.
        
        Args:
            enabled_packs: List of pack IDs to load. If None, load all available
                          based on license tier.
            skip_license_check: For internal/testing use.
        
        Returns:
            List of rule dictionaries.
        """
        all_rules = []
        packs = self.discover_packs()
        
        # Determine which packs to load
        if enabled_packs is None:
            enabled_packs = []
            for pack_id, metadata in packs.items():
                if skip_license_check:
                    enabled_packs.append(pack_id)
                elif validate_license_tier(metadata.license_required):
                    enabled_packs.append(pack_id)
        
        logger.info(f"Loading rules from packs: {enabled_packs}")
        
        # Load each enabled pack
        for pack_id in enabled_packs:
            if pack_id not in packs:
                logger.warning(f"Pack '{pack_id}' not found, skipping")
                continue
            
            try:
                rules = self.load_pack_rules(pack_id)
                all_rules.extend(rules)
                logger.info(f"Successfully loaded {len(rules)} rules from pack '{pack_id}'")
            except LicenseError as e:
                logger.warning(f"Skipping pack '{pack_id}': {e}")
            except Exception as e:
                logger.error(f"Error loading pack '{pack_id}': {e}")
        
        logger.info(f"Total rules loaded: {len(all_rules)}")
        return all_rules


# Global loader instance for convenience
_loader = PackLoader()


def get_pack_loader() -> PackLoader:
    """Get the global pack loader instance."""
    return _loader


def load_rules(
    enabled_packs: Optional[List[str]] = None,
    skip_license_check: bool = False
) -> List[Dict[str, Any]]:
    """Convenience function using the global loader."""
    return _loader.load_rules(enabled_packs, skip_license_check)


def list_available_packs() -> Dict[str, PackMetadata]:
    """List all available packs."""
    return _loader.discover_packs()
