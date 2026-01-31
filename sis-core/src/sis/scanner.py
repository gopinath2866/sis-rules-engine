"""
SIS Scanner
"""
import os
from typing import List, Dict, Any
from .parsers.terraform_simple_fixed import parse_terraform_simple
from .engine import validate_resources

class Scanner:
    """SIS Scanner"""
    
    def scan(self, target: str, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scan a target file or directory against given rules.
        
        Args:
            target: Path to file or directory
            rules: List of rules to check against
        
        Returns:
            List of violations found
        """
        # For now, only handle single files
        if not os.path.exists(target):
            return []
        
        if os.path.isdir(target):
            return []
        
        # Check file extension
        if not target.endswith('.tf'):
            return []
        
        # Read and parse the file
        with open(target, 'r') as f:
            content = f.read()
        
        # Parse Terraform content
        resources = parse_terraform_simple(content)
        
        # Add file path to each resource for reporting
        for resource in resources:
            resource['file_path'] = target
        
        # Validate resources against rules
        violations = validate_resources(resources, rules)
        
        return violations
