"""
Simple Terraform parser that preserves nested block structure
"""
import re
import json
from typing import Dict, Any, List

def parse_terraform_simple(content: str) -> List[Dict[str, Any]]:
    """
    Parse Terraform HCL2 content, preserving nested block structure.
    
    Args:
        content: Terraform HCL2 content
    
    Returns:
        List of resources with their configurations
    """
    resources = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for resource definitions
        resource_match = re.match(r'resource\s+"([^"]+)"\s+"([^"]+)"\s*{', line)
        if resource_match:
            resource_type = resource_match.group(1)
            resource_name = resource_match.group(2)
            
            # Find the matching closing brace
            brace_count = 1
            j = i + 1
            resource_lines = []
            
            while j < len(lines) and brace_count > 0:
                resource_lines.append(lines[j])
                if '{' in lines[j]:
                    brace_count += 1
                if '}' in lines[j]:
                    brace_count -= 1
                j += 1
            
            # Parse the resource block
            resource_content = '\n'.join(resource_lines[:-1])  # Exclude the closing brace
            attributes = parse_resource_block(resource_content)
            
            resources.append({
                'kind': resource_type,
                'name': resource_name,
                'attributes': attributes,
                'line': i + 1  # 1-based line number
            })
            
            i = j - 1  # Skip to after the resource
        
        i += 1
    
    return resources

def parse_resource_block(content: str) -> Dict[str, Any]:
    """
    Parse a resource block, handling nested structures.
    """
    attributes = {}
    lines = content.strip().split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            i += 1
            continue
        
        # Check for nested blocks (like lifecycle, provisioner, etc.)
        block_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_-]*)\s*{', line)
        if block_match:
            block_name = block_match.group(1)
            
            # Find the matching closing brace
            brace_count = 1
            j = i + 1
            block_lines = []
            
            while j < len(lines) and brace_count > 0:
                block_lines.append(lines[j])
                if '{' in lines[j]:
                    brace_count += 1
                if '}' in lines[j]:
                    brace_count -= 1
                j += 1
            
            # Parse the nested block
            block_content = '\n'.join(block_lines[:-1])
            block_attrs = parse_block(block_content)
            
            # Store the nested block
            if block_name in attributes:
                # Convert to list if multiple blocks of same type
                if isinstance(attributes[block_name], list):
                    attributes[block_name].append(block_attrs)
                else:
                    attributes[block_name] = [attributes[block_name], block_attrs]
            else:
                attributes[block_name] = block_attrs
            
            i = j - 1
        
        else:
            # Parse simple attribute assignments
            attr_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_-]*)\s*=\s*(.+)$', line)
            if attr_match:
                key = attr_match.group(1)
                value = parse_value(attr_match.group(2).strip())
                attributes[key] = value
        
        i += 1
    
    return attributes

def parse_block(content: str) -> Dict[str, Any]:
    """
    Parse a nested block (like lifecycle).
    """
    block_attrs = {}
    lines = content.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        attr_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_-]*)\s*=\s*(.+)$', line)
        if attr_match:
            key = attr_match.group(1)
            value = parse_value(attr_match.group(2).strip())
            block_attrs[key] = value
    
    return block_attrs

def parse_value(value_str: str) -> Any:
    """
    Parse a Terraform value string into a Python value.
    """
    # Remove trailing commas
    value_str = value_str.rstrip(',')
    
    # Try to parse as JSON (for complex values)
    try:
        return json.loads(value_str)
    except:
        pass
    
    # Handle booleans
    if value_str.lower() == 'true':
        return True
    elif value_str.lower() == 'false':
        return False
    
    # Handle numbers
    try:
        return int(value_str)
    except:
        try:
            return float(value_str)
        except:
            pass
    
    # Remove quotes from strings
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    # Return as-is
    return value_str

# For backward compatibility
parse_terraform = parse_terraform_simple
