"""Premium compliance rules (GDPR, HIPAA, PCI-DSS, SOC2)"""

GDPR_RULES = [
    {
        "id": "gdpr-001",
        "name": "GDPR Data Location",
        "description": "Ensure personal data is stored in GDPR-compliant regions",
        "category": "compliance",
        "severity": "high",
        "condition": {
            "resource_type": "*",
            "field": "location",
            "operator": "IN",
            "value": ["eu-west-1", "eu-central-1", "europe-west1"]
        }
    },
    {
        "id": "gdpr-002",
        "name": "Data Encryption Required",
        "description": "Personal data must be encrypted at rest and in transit",
        "category": "compliance",
        "severity": "high",
        "condition": {
            "resource_type": "*",
            "field": "encryption.enabled",
            "operator": "EQUALS",
            "value": True
        }
    }
]

HIPAA_RULES = [
    {
        "id": "hipaa-001",
        "name": "HIPAA Audit Logging",
        "description": "Ensure audit logging is enabled for healthcare data",
        "category": "compliance",
        "severity": "high",
        "condition": {
            "resource_type": "*",
            "field": "logging.enabled",
            "operator": "EQUALS",
            "value": True
        }
    }
]

PCI_DSS_RULES = [
    {
        "id": "pci-001",
        "name": "PCI DSS Firewall Rules",
        "description": "Ensure firewall rules comply with PCI DSS requirements",
        "category": "compliance",
        "severity": "critical",
        "condition": {
            "resource_type": "firewall",
            "field": "rules",
            "operator": "VALIDATE",
            "value": "pci_compliance"
        }
    }
]

# Export all premium rules
PREMIUM_RULES = GDPR_RULES + HIPAA_RULES + PCI_DSS_RULES
