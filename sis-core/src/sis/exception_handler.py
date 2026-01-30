"""
Exception Handler - Governance boundary enforcement.
Validates exception artifacts but NEVER modifies findings.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Optional, List, Tuple
import sys


class ExceptionHandler:
    """Handles exception validation with strict invariants."""
    
    # These invariants cannot be violated
    INVARIANTS = [
        "does_not_mark_safe",
        "does_not_modify_findings", 
        "audit_visibility"
    ]
    
    @staticmethod
    def validate_exception(exception_path: str, gate: str, violations: List[Dict]) -> Optional[Dict]:
        """
        Validate exception against schema and invariants.
        Returns validated exception data if valid, None otherwise.
        """
        try:
            with open(exception_path, 'r') as f:
                exception_data = json.load(f)
        except Exception as e:
            print(f"⚠️  Exception artifact ignored (failed to read): {e}", file=sys.stderr)
            return None
        
        try:
            # 1. Schema version check
            if exception_data.get('schema_version') != '1.0':
                print(f"⚠️  Exception artifact ignored (unsupported schema version)", file=sys.stderr)
                return None
            
            # 2. Enforcement effect must be ACKNOWLEDGED_ONLY
            if exception_data.get('enforcement_effect') != 'ACKNOWLEDGED_ONLY':
                print(f"⚠️  Exception artifact ignored (invalid enforcement effect)", file=sys.stderr)
                return None
            
            # 3. Gate must match (if exception specifies a gate)
            exception_gate = exception_data.get('sis_report', {}).get('gate')
            if exception_gate and exception_gate != gate:
                print(f"⚠️  Exception artifact ignored (gate mismatch: expected {gate}, got {exception_gate})", file=sys.stderr)
                return None
            
            # 4. Must not be expired
            expires_at = exception_data.get('validity', {}).get('expires_at')
            if expires_at:
                try:
                    # Handle both with and without Z suffix
                    if expires_at.endswith('Z'):
                        expiry = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    else:
                        expiry = datetime.fromisoformat(expires_at)
                    
                    if expiry < datetime.now(expiry.tzinfo):
                        print(f"⚠️  Exception artifact ignored (expired at {expires_at})", file=sys.stderr)
                        return None
                except ValueError:
                    print(f"⚠️  Exception artifact ignored (invalid expiry format)", file=sys.stderr)
                    return None
            
            # 5. Max duration check
            max_days = exception_data.get('validity', {}).get('max_duration_days')
            if max_days and max_days > 90:
                print(f"⚠️  Exception artifact ignored (duration exceeds 90 days)", file=sys.stderr)
                return None
            
            # 6. Invariants must be present and true
            invariants = exception_data.get('invariants', {})
            for invariant in ExceptionHandler.INVARIANTS:
                if not invariants.get(invariant):
                    print(f"⚠️  Exception artifact ignored (invariant violation: {invariant})", file=sys.stderr)
                    return None
            
            # 7. Signature must be present (but not verified in v1)
            if not exception_data.get('signature', {}).get('required', True):
                print(f"⚠️  Exception artifact ignored (signature not required)", file=sys.stderr)
                return None
            
            # 8. Verify exception_id is content-addressed (basic check)
            exception_id = exception_data.get('exception_id', '')
            if not exception_id.startswith('sha256(') or not exception_id.endswith(')'):
                print(f"⚠️  Exception artifact ignored (invalid exception_id format)", file=sys.stderr)
                return None
            
            # 9. Check if exception matches at least one violation
            rule_id = exception_data.get('scope', {}).get('rule_id')
            target = exception_data.get('scope', {}).get('target')
            
            if not rule_id or not target:
                print(f"⚠️  Exception artifact ignored (missing rule_id or target in scope)", file=sys.stderr)
                return None
            
            has_matching_violation = False
            for violation in violations:
                if (violation.get('rule_id') == rule_id and 
                    violation.get('target') == target):
                    has_matching_violation = True
                    break
            
            if not has_matching_violation:
                print(f"⚠️  Exception artifact ignored (no matching violation for rule {rule_id} on target {target})", file=sys.stderr)
                return None
            
            return exception_data
            
        except Exception as e:
            print(f"⚠️  Exception artifact ignored (validation error: {e})", file=sys.stderr)
            return None
    
    @staticmethod
    def get_governance_output(exception_data: Dict) -> Tuple[str, Dict]:
        """Generate governance output for valid exception."""
        rule_id = exception_data.get('scope', {}).get('rule_id', 'unknown')
        expires_at = exception_data.get('validity', {}).get('expires_at', 'unknown')
        exception_id = exception_data.get('exception_id', 'unknown')
        
        # CLI output
        cli_output = (
            "\n" + "─" * 60 + "\n"
            "Governance Record Acknowledged\n"
            f"Exception ID: {exception_id}\n"
            f"Rule: {rule_id}\n"
            f"Status: ACKNOWLEDGED_ONLY\n"
            f"Expires: {expires_at}\n\n"
            "Note:\n"
            "This exception records explicit risk acceptance.\n"
            "It does not alter SIS findings or enforcement.\n"
            "─" * 60
        )
        
        # JSON output
        json_output = {
            "exception_acknowledged": True,
            "exception_id": exception_id,
            "enforcement_effect": "ACKNOWLEDGED_ONLY",
            "expires_at": expires_at
        }
        
        return cli_output, json_output
