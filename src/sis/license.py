"""License validation for premium features"""

import hashlib
import datetime
import json
from typing import Optional, Dict, Any

class LicenseValidator:
    """Validate and manage software licenses"""
    
    def __init__(self):
        self.license_key = None
        self.license_data = None
        
    def validate_license(self, license_key: str) -> Dict[str, Any]:
        """Validate a license key and return license data"""
        try:
            if license_key.startswith("SIS-PRO-") and len(license_key) == 32:
                return {
                    "valid": True,
                    "tier": "pro",
                    "expires": "2025-12-31",
                    "features": ["compliance_rules", "custom_rule_builder"]
                }
            elif license_key.startswith("SIS-ENT-") and len(license_key) == 32:
                return {
                    "valid": True,
                    "tier": "enterprise",
                    "expires": "2025-12-31",
                    "features": ["compliance_rules", "custom_rule_builder", "on_premise_deployment", "sso_integration"]
                }
            else:
                return {
                    "valid": False,
                    "error": "Invalid license key format"
                }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def load_license(self, license_file: str = "sis_license.key") -> bool:
        """Load license from file"""
        try:
            with open(license_file, 'r') as f:
                self.license_key = f.read().strip()
                self.license_data = self.validate_license(self.license_key)
                return self.license_data.get("valid", False)
        except FileNotFoundError:
            self.license_data = {"valid": False, "tier": "free"}
            return True
        except Exception as e:
            print(f"Error loading license: {e}")
            self.license_data = {"valid": False, "tier": "free"}
            return True
    
    def has_feature(self, feature_name: str) -> bool:
        """Check if current license has a specific feature"""
        if not self.license_data:
            self.load_license()
        
        if self.license_data.get("tier") == "free":
            free_features = ["basic_validation", "community_rules", "cli_interface"]
            return feature_name in free_features
        elif self.license_data.get("tier") == "pro":
            pro_features = ["basic_validation", "community_rules", "cli_interface",
                          "compliance_rules", "custom_rule_builder"]
            return feature_name in pro_features
        elif self.license_data.get("tier") == "enterprise":
            return True
        
        return False
    
    def get_license_info(self) -> Dict[str, Any]:
        """Get information about current license"""
        if not self.license_data:
            self.load_license()
        
        return {
            "tier": self.license_data.get("tier", "free"),
            "valid": self.license_data.get("valid", False),
            "expires": self.license_data.get("expires", None),
            "features": self.license_data.get("features", [])
        }

license_validator = LicenseValidator()

def check_license(feature: str = None) -> bool:
    """Check if a feature is licensed (public interface)"""
    if feature is None:
        return license_validator.get_license_info()["valid"]
    return license_validator.has_feature(feature)

def get_license_tier() -> str:
    """Get current license tier"""
    return license_validator.get_license_info()["tier"]
