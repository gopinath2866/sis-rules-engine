"""Parser dispatcher for SIS."""
from .terraform import parse_file as parse_terraform
from .cloudformation import parse_file as parse_cloudformation
from .kubernetes import parse_file as parse_kubernetes
from .docker_compose import parse_file as parse_docker_compose
from .arm import parse_file as parse_arm

def parse_file(file_type: str, content: str):
    """
    Dispatch parsing based on file type.
    Returns a list of dicts, each containing:
    - kind: resource type
    - name: resource name
    - line: line number (if available)
    - data: parsed resource data
    """
    if file_type == "terraform":
        return parse_terraform(content)
    elif file_type == "cloudformation":
        return parse_cloudformation(content)
    elif file_type == "kubernetes":
        return parse_kubernetes(content)
    elif file_type == "docker_compose":
        return parse_docker_compose(content)
    elif file_type == "arm":
        return parse_arm(content)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")