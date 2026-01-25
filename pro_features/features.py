"""Feature flag system for premium features"""

FEATURE_FLAGS = {
    "free": {
        "basic_validation": True,
        "terraform_support": True,
        "community_rules": True,
        "cli_interface": True
    },
    "pro": {
        "compliance_rules": True,
        "custom_rule_builder": True,
        "api_rate_limits": True,
        "advanced_parsers": True
    },
    "enterprise": {
        "on_premise_deployment": True,
        "sso_integration": True,
        "custom_parsers": True,
        "priority_support": True,
        "training_included": True
    }
}

def check_feature(feature_name, license_tier="free"):
    """Check if a feature is available for the given license tier"""
    if license_tier in FEATURE_FLAGS:
        return FEATURE_FLAGS[license_tier].get(feature_name, False)
    return False

def get_available_features(license_tier="free"):
    """Get all available features for a license tier"""
    features = []
    for tier in ["free", "pro", "enterprise"]:
        if tier == license_tier or (tier == "free" and license_tier in ["pro", "enterprise"]):
            for feature, enabled in FEATURE_FLAGS[tier].items():
                if enabled:
                    features.append(feature)
    return features
