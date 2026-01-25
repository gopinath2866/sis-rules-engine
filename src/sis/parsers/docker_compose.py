"""
Docker Compose parser for SIS
"""

from typing import Any, Dict, List, Optional

import yaml


def parse_docker_compose(
    content: str, file_format: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Parse Docker Compose file and extract security-relevant configurations.

    Args:
        content: Docker Compose YAML content
        file_format: Optional format specifier (unused for Docker Compose)

    Returns:
        List of extracted resources
    """
    resources: List[Dict[str, Any]] = []

    try:
        config = yaml.safe_load(content)

        if not isinstance(config, dict):
            return resources

        # Check for services
        services = config.get("services", {})

        for service_name, service_config in services.items():
            if isinstance(service_config, dict):
                # Check for security-relevant configurations
                if "privileged" in service_config or "cap_add" in service_config:
                    resources.append(
                        {
                            "name": service_name,
                            "type": "docker_service",
                            "config": service_config,
                            "source": "docker_compose",
                        }
                    )

        return resources
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse Docker Compose YAML: {str(e)}")
