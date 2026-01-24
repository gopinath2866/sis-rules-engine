"""
Test SIS API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.sis.api.endpoints import app

# Create test client with the app
client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_get_rules():
    """Test rules endpoint"""
    response = client.get("/rules")
    assert response.status_code == 200
    data = response.json()
    assert "rules" in data
    assert isinstance(data["rules"], list)

def test_validate_endpoint():
    """Test validate endpoint with sample data"""
    test_files = [
        {
            "path": "test.tf",
            "content": """
resource "aws_s3_bucket" "public_bucket" {
  bucket = "test-bucket"
  acl    = "public-read"
}
""",
            "type": "terraform"
        }
    ]
    
    response = client.post("/validate", json={"files": test_files})
    assert response.status_code == 200
    data = response.json()
    assert "findings" in data
    assert "summary" in data
    assert "errors" in data

def test_validate_with_invalid_file():
    """Test validate with invalid file"""
    test_files = [
        {
            "path": "test.txt",
            "content": "not a valid file",
            "type": "unknown"
        }
    ]
    
    response = client.post("/validate", json={"files": test_files})
    # Should handle gracefully
    assert response.status_code == 200
    data = response.json()
    assert "errors" in data
