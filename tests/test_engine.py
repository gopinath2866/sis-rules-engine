"""
Test the SIS engine
"""
import pytest
from src.sis.engine import validate_resources, check_condition

def test_check_condition():
    """Test condition checking"""
    resource = {
        "name": "test_resource",
        "type": "aws_s3_bucket",
        "properties": {"versioning": {"enabled": True}}
    }
    
    # Test EQUALS operator
    condition = {"path": "type", "operator": "EQUALS", "value": "aws_s3_bucket"}
    assert check_condition(resource, condition) == True
    
    # Test NOT_EQUALS operator
    condition = {"path": "type", "operator": "NOT_EQUALS", "value": "aws_iam_user"}
    assert check_condition(resource, condition) == True
    
    # Test EXISTS operator
    condition = {"path": "name", "operator": "EXISTS"}
    assert check_condition(resource, condition) == True
    
    # Test nested path
    condition = {"path": "properties.versioning.enabled", "operator": "EQUALS", "value": True}
    assert check_condition(resource, condition) == True

def test_validate_resources_empty():
    """Test validation with empty resources"""
    rules = []
    resources = []
    violations = validate_resources(resources, rules)
    assert violations == []

def test_validate_resources_with_rule():
    """Test validation with a simple rule"""
    rules = [
        {
            "rule_id": "TEST-01",
            "rule_type": "TEST",
            "applies_to": {
                "resource_kinds": ["aws_s3_bucket"]
            },
            "detection": {
                "match_logic": "ALL",
                "conditions": [
                    {"path": "type", "operator": "EQUALS", "value": "aws_s3_bucket"}
                ]
            },
            "message": "Test rule violation",
            "severity": "medium"
        }
    ]
    
    resources = [
        {"name": "bucket1", "type": "aws_s3_bucket"},
        {"name": "user1", "type": "aws_iam_user"}
    ]
    
    violations = validate_resources(resources, rules)
    assert len(violations) == 1
    assert violations[0]["rule_id"] == "TEST-01"
    assert violations[0]["resource_id"] == "bucket1"
