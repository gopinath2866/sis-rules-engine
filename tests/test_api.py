import requests
import time

BASE_URL = "http://localhost:8000/v1/scan"

def test_api_health_and_basic_scan():
    payload = {
        "files": [
            {
                "name": "basic.tf",
                "type": "terraform",
                "content": 'resource "aws_s3_bucket" "test" {}'
            }
        ]
    }

    r = requests.post(
        BASE_URL,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": "test"
        },
        json=payload,
        timeout=5
    )

    assert r.status_code == 200

    body = r.json()

    # Required top-level fields
    assert "scan_id" in body
    assert "timestamp" in body
    assert body["scanner_version"] == "1.0.0"
    assert "findings" in body
    assert "summary" in body

    # Determinism checks
    assert isinstance(body["findings"], list)
    assert body["summary"]["total_files"] == 1
