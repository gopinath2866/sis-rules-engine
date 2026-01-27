"""
JWT-based license validation for rule packs.
"""
import json
import os
import logging
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

logger = logging.getLogger(__name__)

# Built-in public key (embedded in binary)
# Generated with: generate_keys.py
BUILTIN_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAw7hQwH0jB0XqCvQ6Qr8Y
q9ZqD8QvZ2W8QJ8q3gL7vL8qKq0L8QvZ2W8QJ8q3gL7vL8qKq0L8QvZ2W8QJ8q3
gL7vL8qKq0L8QvZ2W8QJ8q3gL7vL8qKq0L8QvZ2W8QJ8q3gL7vL8qKq0L8QvZ2W
8QJ8q3gL7vL8qKq0L8QvZ2W8QJ8q3gL7vL8qKq0L8QvZ2W8QJ8q3gL7vL8qKq0L
8QvZ2W8QJ8q3gL7vL8qKq0L8QvZ2W8QJ8q3gL7vL8qKq0L8QvZ2W8QIDAQAB
-----END PUBLIC KEY-----"""


class LicenseError(Exception):
    """Raised when license validation fails."""
    pass


class LicenseManager:
    """Manage JWT-based license validation."""
    
    def __init__(self, license_dir: Optional[Path] = None):
        self.license_dir = license_dir or Path.home() / '.sis' / 'licenses'
        self.licenses: Dict[str, Dict[str, Any]] = {}
        self._public_key = self._load_public_key()
        self._load_licenses()
    
    def _load_public_key(self):
        """Load public key for verification."""
        try:
            # First try environment override (for testing/custom builds)
            env_path = os.environ.get("SIS_PUBLIC_KEY")
            if env_path:
                env_key = Path(env_path).expanduser().resolve()
                if env_key.is_file():
                    key_data = env_key.read_text()
                    logger.debug(f"Loaded public key from environment: {env_key}")
                else:
                    raise LicenseError("SIS_PUBLIC_KEY must point to a PEM file")
            else:
                # Use built-in key
                key_data = BUILTIN_PUBLIC_KEY
                logger.debug("Using built-in public key")
            
            return serialization.load_pem_public_key(key_data.encode())
        except Exception as e:
            logger.error(f"Failed to load public key: {e}")
            raise LicenseError(f"Invalid public key configuration: {e}")
    
    def _load_licenses(self):
        """Load and validate all license JWT files."""
        if not self.license_dir.exists():
            self.license_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created license directory: {self.license_dir}")
            return
        
        for license_file in self.license_dir.glob('*.jwt'):
            try:
                with open(license_file, 'r') as f:
                    token = f.read().strip()
                
                payload = self._validate_jwt(token)
                if payload:
                    tier = payload.get('tier', 'unknown')
                    self.licenses[tier] = payload
                    
                    # Log fingerprint for debugging (not full token)
                    fingerprint = hashlib.sha256(token.encode()).hexdigest()[:8]
                    logger.info(f"Loaded license {fingerprint} for tier: {tier}")
            except Exception as e:
                logger.warning(f"Invalid license file {license_file}: {e}")
    
    def _validate_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token and return payload if valid.
        
        JWT Claims expected:
        - sub: customer ID (required)
        - tier: license tier (required, one of: free|pro|enterprise)
        - exp: expiration timestamp (optional)
        - allowed_packs: list of pack IDs (optional, empty/missing = all)
        - iss: "Static Irreversibility Scanner" (optional but validated if present)
        - name: customer name (optional)
        """
        try:
            # Decode and verify with RS256
            payload = jwt.decode(
                token,
                self._public_key,
                algorithms=['RS256'],
                options={
                    'verify_exp': True,
                    'verify_aud': False,
                    'require': ['sub', 'tier']
                }
            )
            
            # Additional validation
            if not payload.get('tier') in ['free', 'pro', 'enterprise']:
                raise jwt.InvalidTokenError("Invalid tier")
            
            # Validate issuer if present
            if 'iss' in payload and payload['iss'] != 'Static Irreversibility Scanner':
                raise jwt.InvalidTokenError("Invalid issuer")
            
            # Ensure allowed_packs is a list if present
            if 'allowed_packs' in payload and not isinstance(payload['allowed_packs'], list):
                raise jwt.InvalidTokenError("allowed_packs must be a list")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("License has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid license token: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error validating license: {e}")
            return None
    
    def has_tier(self, required_tier: str) -> bool:
        """Check if user has a valid license for the required tier."""
        if required_tier == 'free':
            return True
        
        # Check direct tier match
        if required_tier in self.licenses:
            return True
        
        # Enterprise implies pro access
        if required_tier == 'pro' and 'enterprise' in self.licenses:
            return True
        
        return False
    
    def allows_pack(self, pack_id: str) -> bool:
        """
        Check if any valid license allows this specific pack.
        
        Rules:
        1. Free packs (license_required='free') always allowed
        2. If license has no allowed_packs field or empty list → all packs for that tier
        3. If allowed_packs is non-empty → pack must be in list
        4. Enterprise license allows all pro packs (unless restricted by allowed_packs)
        """
        # First, check if we have any valid license that could allow it
        for tier, payload in self.licenses.items():
            allowed_packs = payload.get('allowed_packs')
            
            # No allowed_packs field → all packs for this tier
            if allowed_packs is None:
                return True
            
            # Empty list → all packs for this tier
            if len(allowed_packs) == 0:
                return True
            
            # Pack is explicitly allowed
            if pack_id in allowed_packs:
                return True
        
        return False
    
    def get_license_info(self, tier: str) -> Optional[Dict[str, Any]]:
        """Get license information for display."""
        if tier not in self.licenses:
            return None
        
        payload = self.licenses[tier]
        expires_at = datetime.fromtimestamp(payload['exp']) if 'exp' in payload else None
        
        return {
            'tier': payload['tier'],
            'customer': payload.get('sub', 'Unknown'),
            'issued_to': payload.get('name', 'Unknown'),
            'expires_at': expires_at.isoformat() if expires_at else None,
            'days_remaining': (expires_at - datetime.utcnow()).days if expires_at else None,
            'allowed_packs': payload.get('allowed_packs', [])
        }


# Global license manager (lazy-loaded)
_license_manager: Optional[LicenseManager] = None


def get_license_manager() -> LicenseManager:
    """Get or create the global license manager instance (lazy)."""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
    return _license_manager


def validate_license_tier(required_tier: str) -> bool:
    """Check if user has a valid license for the required tier."""
    return get_license_manager().has_tier(required_tier)


def get_license_info(tier: str) -> Optional[Dict[str, Any]]:
    """Get license information."""
    return get_license_manager().get_license_info(tier)
