"""
Critical regression test for array semantics.
This test would have failed in v1.0 (checking only first element).
Must never be removed - serves as a "security semantics canary".
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from sis.engine import check_condition

def test_array_existential_semantics_security_regression():
    """
    Test that would have failed in v1.0.
    Security rule: Detect if ANY container is privileged.
    In v1.0, this would only check first container, missing security issues.
    """
    # Simulated Kubernetes pod with first container safe, second vulnerable
    vulnerable_pod = {
        "spec": {
            "containers": [
                {
                    "name": "safe-container",
                    "securityContext": {"privileged": False}  # Safe
                },
                {
                    "name": "vulnerable-container",
                    "securityContext": {"privileged": True}  # Security issue!
                }
            ]
        }
    }
    
    # Security rule: ANY container privileged
    security_rule = {
        "path": "spec.containers[].securityContext.privileged",
        "operator": "EQUALS",
        "value": "true"
    }
    
    result = check_condition(vulnerable_pod, security_rule)
    
    # This MUST be True - second container is privileged
    # In v1.0, this would return False (only checked first container)
    assert result == True, (
        "CRITICAL SECURITY REGRESSION: "
        "Array existential semantics not working. "
        "Would miss security issues in non-first array elements."
    )
    
    # Also test empty array (should return False)
    empty_pod = {"spec": {"containers": []}}
    empty_result = check_condition(empty_pod, security_rule)
    assert empty_result == False, "Empty array should return False for EQUALS operator"
    
    print("✅ CRITICAL REGRESSION TEST PASSED: Array existential semantics working correctly")

def test_nested_array_security_regression():
    """
    Test nested arrays - another v1.0 failure scenario.
    """
    resource = {
        "network": {
            "rules": [
                {"ports": [80, 443]},      # Safe ports
                {"ports": [22, 3389]},     # Security risk: 22 (SSH) and 3389 (RDP)
            ]
        }
    }
    
    # Check if ANY rule has ANY dangerous port
    dangerous_rule = {
        "path": "network.rules[].ports[]",
        "operator": "EQUALS",
        "value": "22"  # SSH port
    }
    
    result = check_condition(resource, dangerous_rule)
    assert result == True, (
        "CRITICAL SECURITY REGRESSION: "
        "Nested array semantics not working. "
        "Would miss security issues in nested structures."
    )

if __name__ == "__main__":
    test_array_existential_semantics_security_regression()
    test_nested_array_security_regression()
    print("\n" + "="*60)
    print("ALL CRITICAL REGRESSION TESTS PASSED")
    print("Array semantics fix is preserving security scanning correctness")
    print("="*60)
