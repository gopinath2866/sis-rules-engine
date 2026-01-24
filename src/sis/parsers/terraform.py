"""
Terraform parser for SIS - Uses improved simple parser
"""
from typing import Dict, Any, List, Optional
from .terraform_simple import parse_terraform_simple

def parse_terraform(content: str, file_format: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Parse Terraform files using our improved simple parser
    
    Args:
        content: Terraform HCL2 content
        file_format: Optional format specifier
    
    Returns:
        List of extracted resources with their configurations
    """
    try:
        # Try using our improved simple parser
        return parse_terraform_simple(content)
    except Exception as e:
        print(f"⚠️  Terraform parsing failed: {e}")
        return []
