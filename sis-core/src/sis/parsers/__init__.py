"""
Parser module for SIS - Static Irreversibility Scanner
"""

from typing import Dict, Any, List, Optional


def parse_content(content: str, file_type: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Parse content based on file type and return normalized resources.
    
    Args:
        content: The file content to parse
        file_type: Type of file (terraform, kubernetes, docker_compose, etc.)
        **kwargs: Additional arguments for parsers
    
    Returns:
        List of extracted resources with their configurations
    """
    if file_type == 'terraform':
        from .terraform import parse_terraform
        return parse_terraform(content, **kwargs)
    elif file_type == 'kubernetes':
        from .kubernetes import parse_kubernetes
        return parse_kubernetes(content, **kwargs)
    elif file_type == 'docker_compose':
        from .docker_compose import parse_docker_compose
        return parse_docker_compose(content, **kwargs)
    elif file_type == 'cloudformation':
        from .cloudformation import parse_cloudformation
        return parse_cloudformation(content, **kwargs)
    elif file_type == 'arm':
        from .arm import parse_arm
        return parse_arm(content, **kwargs)
    elif file_type == 'terraform_simple':
        from .terraform_simple import parse_terraform_simple
        return parse_terraform_simple(content, **kwargs)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


# Try to import the parser functions for direct access
# These will be available if the modules exist
try:
    from .terraform import parse_terraform
except ImportError:
    parse_terraform = None

try:
    from .kubernetes import parse_kubernetes
except ImportError:
    parse_kubernetes = None

try:
    from .docker_compose import parse_docker_compose
except ImportError:
    parse_docker_compose = None

try:
    from .cloudformation import parse_cloudformation
except ImportError:
    parse_cloudformation = None

try:
    from .arm import parse_arm
except ImportError:
    parse_arm = None

try:
    from .terraform_simple import parse_terraform_simple
except ImportError:
    parse_terraform_simple = None

__all__ = [
    'parse_content',
    'parse_terraform',
    'parse_kubernetes',
    'parse_docker_compose',
    'parse_cloudformation',
    'parse_arm',
    'parse_terraform_simple'
]
