"""
Simple but reliable Terraform parser for SIS
"""

import json
import re
from typing import Any, Dict, List, Optional


def parse_terraform_simple(content: str) -> List[Dict[str, Any]]:
    """
    Simple but reliable Terraform parser using regex
    """
    resources = []
    lines = content.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for resource definitions
        if line.startswith("resource "):
            # Extract resource type and name
            match = re.match(r'resource\s+"([^"]+)"\s+"([^"]+)"', line)
            if match:
                resource_type = match.group(1)
                resource_name = match.group(2)

                # Find the start of the block
                start_line = i
                brace_count = 0
                in_block = False
                block_lines = []

                # Find the entire resource block
                for j in range(i, len(lines)):
                    current_line = lines[j]
                    block_lines.append(current_line)

                    # Count braces
                    for char in current_line:
                        if char == "{":
                            brace_count += 1
                            in_block = True
                        elif char == "}":
                            brace_count -= 1

                    if in_block and brace_count == 0:
                        # End of block found
                        block_content = "\n".join(block_lines)
                        config = _parse_simple_block(block_content)

                        resource = {
                            "kind": resource_type,
                            "name": resource_name,
                            "config": config,
                            "line": start_line + 1,
                            "source": "terraform",
                            "raw": block_content,
                        }

                        # Extract common attributes
                        for key in ["acl", "lifecycle", "policy", "ingress", "egress"]:
                            if key in config:
                                resource[key] = config[key]

                        resources.append(resource)
                        i = j  # Skip to end of block
                        break
                else:
                    # Block not properly closed
                    i += 1
                    continue
        elif line.startswith("variable "):
            # Parse variables for secrets
            match = re.match(r'variable\s+"([^"]+)"', line)
            if match:
                var_name = match.group(1)
                var_config = {}

                # Find variable block
                start_line = i
                brace_count = 0
                in_block = False
                block_lines = []

                for j in range(i, len(lines)):
                    current_line = lines[j]
                    block_lines.append(current_line)

                    for char in current_line:
                        if char == "{":
                            brace_count += 1
                            in_block = True
                        elif char == "}":
                            brace_count -= 1

                    if in_block and brace_count == 0:
                        block_content = "\n".join(block_lines)
                        var_config = _parse_simple_block(block_content)

                        resource = {
                            "kind": "variable",
                            "name": var_name,
                            "config": var_config,
                            "line": start_line + 1,
                            "source": "terraform",
                        }

                        if "default" in var_config:
                            resource["default"] = var_config["default"]

                        resources.append(resource)
                        i = j
                        break
                else:
                    i += 1
                    continue
        i += 1

    return resources


def _parse_simple_block(block: str) -> Dict[str, Any]:
    """Parse a simple block into key-value pairs"""
    config = {}
    lines = block.split("\n")

    # Remove the first line (resource definition)
    if lines:
        lines = lines[1:]

    # Remove the last line (closing brace)
    if lines:
        lines = lines[:-1]

    current_key = None
    current_value_lines = []
    in_subblock = False
    subblock_brace_count = 0

    for line in lines:
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            continue

        # Check if we're starting a subblock
        if "{" in line and not in_subblock:
            # Start of a subblock
            key_match = re.match(r"(\w+)\s*{", stripped)
            if key_match:
                current_key = key_match.group(1)
                in_subblock = True
                subblock_brace_count = line.count("{") - line.count("}")
                subblock_lines = [line]
                continue

        # If we're in a subblock, collect lines
        if in_subblock:
            subblock_lines.append(line)
            subblock_brace_count += line.count("{")
            subblock_brace_count -= line.count("}")

            if subblock_brace_count == 0:
                # End of subblock
                subblock_content = "\n".join(subblock_lines)
                config[current_key] = _parse_simple_block(subblock_content)
                in_subblock = False
                current_key = None
                continue

        # Parse key = value pairs
        if "=" in line and not in_subblock:
            parts = line.split("=", 1)
            key = parts[0].strip()
            value = parts[1].strip().rstrip(";")

            # Clean up value
            value = _clean_value(value)

            config[key] = value

    return config


def _clean_value(value: str) -> Any:
    """Clean and convert a value"""
    # Remove comments
    if "#" in value:
        value = value.split("#")[0].strip()

    # Remove surrounding quotes
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        value = value[1:-1]

    # Handle JSON encode
    if value.startswith("jsonencode(") and value.endswith(")"):
        json_str = value[11:-1]  # Remove jsonencode()
        try:
            return json.loads(json_str)
        except:
            return value

    # Handle booleans
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False

    # Handle numbers
    try:
        if "." in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        pass

    # Handle lists (like ["0.0.0.0/0"])
    if value.startswith("[") and value.endswith("]"):
        try:
            # Simple list parsing
            items = value[1:-1].split(",")
            return [_clean_value(item.strip()) for item in items]
        except:
            pass

    return value
