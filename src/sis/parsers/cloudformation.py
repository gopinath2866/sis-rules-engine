"""
CloudFormation template parser for SIS
"""

import json
from typing import Any, Dict, List, Optional

import yaml


def parse_cloudformation(
    content: str, file_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Parse CloudFormation template and extract IAM resources.

    Args:
        content: CloudFormation template content
        file_type: Either 'yaml' or 'json' (defaults to 'yaml' if None)

    Returns:
        List of extracted resources
    """
    resources: List[Dict[str, Any]] = []

    try:
        # Default to yaml if not specified
        if file_type is None:
            file_type = "yaml"

        if file_type.lower() == "yaml":
            template = yaml.safe_load(content)
        elif file_type.lower() == "json":
            template = json.loads(content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        # Extract IAM resources from CloudFormation template
        if isinstance(template, dict) and "Resources" in template:
            for resource_name, resource_def in template["Resources"].items():
                if isinstance(resource_def, dict):
                    resource_type = resource_def.get("Type", "")

                    # Extract IAM resources
                    if "IAM" in resource_type or any(
                        iam_type in resource_type
                        for iam_type in [
                            "AWS::IAM::",
                            "AWS::S3::BucketPolicy",
                            "AWS::SQS::QueuePolicy",
                        ]
                    ):
                        resources.append(
                            {
                                "name": resource_name,
                                "type": resource_type,
                                "properties": resource_def.get("Properties", {}),
                                "source": "cloudformation",
                            }
                        )

        return resources
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to parse CloudFormation template: {str(e)}")
