"""
Parser modules for different infrastructure-as-code formats
"""
from typing import Dict, Any, List, Optional, Callable
from .terraform import parse_terraform
from .kubernetes import parse_kubernetes
from .cloudformation import parse_cloudformation
from .docker_compose import parse_docker_compose
from .arm import parse_arm_template

PARSERS: Dict[str, Callable[[str, Optional[str]], List[Dict[str, Any]]]] = {
    "terraform": lambda content, _: parse_terraform(content),
    "kubernetes": lambda content, _: parse_kubernetes(content),
    "cloudformation": parse_cloudformation,
    "docker_compose": lambda content, _: parse_docker_compose(content),
    "arm": lambda content, _: parse_arm_template(content),
}

def parse_content(
    content: str, 
    file_type: str, 
    file_format: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Parse infrastructure-as-code content based on file type.
    
    Args:
        content: File content as string
        file_type: Type of file (terraform, kubernetes, etc.)
        file_format: Optional format specifier (e.g., 'yaml' for CloudFormation)
    
    Returns:
        List of extracted resources
    
    Raises:
        ValueError: If parser not found or parsing fails
    """
    if file_type not in PARSERS:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    parser = PARSERS[file_type]
    return parser(content, file_format)
