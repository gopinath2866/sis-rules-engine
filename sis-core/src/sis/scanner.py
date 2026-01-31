"""Terraform HCL2 scanner for irreversible patterns."""

from .parsers.terraform_simple import parse_terraform_simple


class Scanner:
    """Scan Terraform files for irreversible infrastructure patterns."""
    
    def scan(self, file_path, rules):
        """Scan a Terraform file for irreversible patterns."""
        findings = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse Terraform content
            resources = parse_terraform_simple(content)
            
            # Check each resource against each rule
            for resource in resources:
                resource_type = resource.get('kind', '')
                resource_name = resource.get('name', '')
                config = resource.get('attributes', {})
                
                for rule in rules:
                    if self._check_rule(rule, config):
                        findings.append({
                            "rule_id": rule.get("rule_id", "UNKNOWN"),
                            "message": rule.get("message", ""),
                            "severity": rule.get("severity", "MEDIUM"),
                            "resource_type": resource_type,
                            "resource_name": resource_name,
                            "file_path": str(file_path),
                            "line": resource.get('line', 1)
                        })
            
        except Exception as e:
            # Don't crash on parse errors
            pass
        
        return findings
    
    def _check_rule(self, rule, config):
        """Check if a rule matches the configuration."""
        rule_id = rule.get("rule_id")
        
        # IRR-DEC-01: deletion_protection = true
        if rule_id == "IRR-DEC-01":
            return config.get("deletion_protection") == True
        
        # IRR-DEC-02: lifecycle.prevent_destroy = true
        if rule_id == "IRR-DEC-02":
            lifecycle = config.get("lifecycle", [{}])[0] if isinstance(config.get("lifecycle"), list) else config.get("lifecycle", {})
            return lifecycle.get("prevent_destroy") == True
        
        # Add more rule checks here as needed
        return False
