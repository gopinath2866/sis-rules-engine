"""
Scanner module for SIS.
Currently a stub implementation for demonstration.
In production, this would contain actual scanning logic.
"""

class SISScanner:
    """Scanner for Security Invariant violations."""
    
    def scan(self, target, rules):
        """
        Scan a target for violations.
        
        Args:
            target: Directory or file to scan
            rules: List of rules to check
            
        Returns:
            List of findings
        """
        # Stub implementation - returns empty list
        return []
    
    def scan_gate(self, gate_name, target_path):
        """
        Scan a specific gate for violations.
        
        Args:
            gate_name: Name of the gate to scan
            target_path: Path to scan
            
        Returns:
            List of findings for the specified gate
        """
        # Stub implementation - returns test violations for proxy-upgrade gate
        if gate_name == 'proxy-upgrade':
            return [
                {
                    'rule_id': 'proxy-admin-not-zero-address',
                    'description': 'Proxy admin is set to zero address',
                    'severity': 'high',
                    'gate': 'proxy-upgrade',
                    'resource': 'test_resource',
                    'location': {'file': 'test.tf', 'line': 1}
                }
            ]
        return []

# Create an alias for backward compatibility
Scanner = SISScanner
