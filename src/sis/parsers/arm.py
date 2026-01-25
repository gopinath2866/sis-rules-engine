"""
Azure Resource Manager (ARM) template parser for SIS
"""

import json
from typing import Any, Dict, List


def parse_arm_template(content: str) -> List[Dict[str, Any]]:
    """
    Parse ARM template and extract IAM resources.

    Args:
        content: ARM template JSON content

    Returns:
        List of extracted resources
    """
    resources = []

    try:
        template = json.loads(content)

        # Extract role definitions from ARM template
        if isinstance(template, dict):
            # Look for role definitions in various locations
            resources_section = template.get("resources", [])
            if isinstance(resources_section, list):
                for resource in resources_section:
                    if isinstance(resource, dict):
                        resource_type = resource.get("type", "")

                        # Extract Azure RBAC resources
                        if any(
                            rbac_type in resource_type
                            for rbac_type in [
                                "Microsoft.Authorization/roleAssignments",
                                "Microsoft.Authorization/roleDefinitions",
                            ]
                        ):
                            resources.append(
                                {
                                    "name": resource.get("name", ""),
                                    "type": resource_type,
                                    "properties": resource.get("properties", {}),
                                    "source": "arm",
                                }
                            )

        return resources
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse ARM template: {str(e)}")
