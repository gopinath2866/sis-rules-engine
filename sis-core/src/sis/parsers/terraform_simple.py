"""
Simple Terraform parser for SIS
"""
import re
from typing import Dict, Any, List, Optional

def parse_terraform_simple(content: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Parse Terraform HCL2 content and extract resources with their attributes.
    
    Args:
        content: Terraform HCL2 content
        **kwargs: Additional arguments
    
    Returns:
        List of extracted resources with their configurations
    """
    resources = []
    
    # If content is empty, return empty list
    if not content or not content.strip():
        return resources
    
    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # Split into lines for processing
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for resource definitions
        if line.startswith('resource'):
            # Extract resource type and name
            match = re.match(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*{', line)
            if match:
                resource_type = match.group(1)
                resource_name = match.group(2)
                
                # Find the matching closing brace
                brace_count = 1
                j = i + 1
                resource_lines = []
                
                while j < len(lines) and brace_count > 0:
                    current_line = lines[j]
                    # Count braces
                    brace_count += current_line.count('{')
                    brace_count -= current_line.count('}')
                    
                    if brace_count > 0:
                        resource_lines.append(current_line)
                    
                    j += 1
                
                # Parse attributes from resource lines
                attributes = {}
                for rline in resource_lines:
                    rline = rline.strip()
                    # Remove comments
                    if '#' in rline:
                        rline = rline.split('#')[0].strip()
                    
                    # Skip empty lines
                    if not rline:
                        continue
                    
                    # Parse key = value pairs
                    if '=' in rline:
                        key_value = rline.split('=', 1)
                        if len(key_value) == 2:
                            key = key_value[0].strip()
                            value = key_value[1].strip()
                            
                            # Remove quotes and clean up
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            
                            attributes[key] = value
                
                # Add the resource
                resources.append({
                    'kind': resource_type,
                    'name': resource_name,
                    'attributes': attributes,
                    'line': i + 1  # Line number where resource starts
                })
                
                i = j  # Skip processed lines
                continue
        
        i += 1
    
    return resources
