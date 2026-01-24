"""
Test SIS API functionality
"""
import pytest
from fastapi.testclient import TestClient
from src.sis.api.endpoints import app

client = TestClient(app)

def test_api_health():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_api_validate_empty():
    """Test validation with empty files"""
    response = client.post("/validate", json={"files": []})
    assert response.status_code == 200
    data = response.json()
    assert "findings" in data
    assert "summary" in data
    assert "errors" in data
    assert data["summary"]["total_resources"] == 0

def test_api_validate_terraform():
    """Test validation with Terraform content"""
    payload = {
        "files": [
            {
                "path": "test.tf",
                "content": 'resource "aws_s3_bucket" "test" {}',
                "type": "terraform"
            }
        ]
    }
    
    response = client.post("/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Should find resources (from our parser stub)
    assert data["summary"]["total_resources"] > 0
    
    # Response should have proper structure
    assert isinstance(data["findings"], list)
    assert isinstance(data["summary"], dict)
    assert isinstance(data["errors"], list)

def test_api_rules_endpoint():
    """Test rules endpoint"""
    response = client.get("/rules")
    assert response.status_code == 200
    data = response.json()
    assert "rules" in data
    assert isinstance(data["rules"], list)
