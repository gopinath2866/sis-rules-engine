#!/bin/bash
echo "🔧 Fixing mypy type errors..."

# Step 1: Install type stubs
echo "Installing type stubs..."
pip install types-PyYAML types-requests types-setuptools

# Step 2: Update the files with proper fixes
echo "Updating source files..."

# Create fixed cloudformation.py
cat > src/sis/parsers/cloudformation.py << 'CFEOF'
"""
CloudFormation template parser for SIS
"""
from typing import Dict, Any, List
import yaml
import json

def parse_cloudformation(content: str, file_type: str = "yaml") -> List[Dict[str, Any]]:
    """
    Parse CloudFormation template and extract IAM resources.
    
    Args:
        content: CloudFormation template content
        file_type: Either 'yaml' or 'json'
    
    Returns:
        List of extracted resources
    """
    resources = []
    
    try:
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
                    if "IAM" in resource_type or any(iam_type in resource_type for iam_type in [
                        "AWS::IAM::", "AWS::S3::BucketPolicy", "AWS::SQS::QueuePolicy"
                    ]):
                        resources.append({
                            "name": resource_name,
                            "type": resource_type,
                            "properties": resource_def.get("Properties", {}),
                            "source": "cloudformation"
                        })
        
        return resources
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to parse CloudFormation template: {str(e)}")
CFEOF

# Create fixed arm.py
cat > src/sis/parsers/arm.py << 'ARMEOF'
"""
Azure Resource Manager (ARM) template parser for SIS
"""
from typing import Dict, Any, List
import json

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
                        if any(rbac_type in resource_type for rbac_type in [
                            "Microsoft.Authorization/roleAssignments",
                            "Microsoft.Authorization/roleDefinitions"
                        ]):
                            resources.append({
                                "name": resource.get("name", ""),
                                "type": resource_type,
                                "properties": resource.get("properties", {}),
                                "source": "arm"
                            })
        
        return resources
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse ARM template: {str(e)}")
ARMEOF

# Create fixed __init__.py for parsers
cat > src/sis/parsers/__init__.py << 'INITEOF'
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
INITEOF

echo "✅ Fixed parser files"

# Step 3: Run mypy to check
echo "Running mypy type checking..."
mypy src/ --ignore-missing-imports

echo "🎉 Type checking complete!"
