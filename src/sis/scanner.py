"""
SIS Unified Scanner - Fixed version
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .engine import validate_resources
from .parsers import parse_content
from .rules.loader import load_rules
# Fail-fast guard: ensure only authoritative loader is used
assert load_rules.__module__ == "sis.rules.loader", \
    "Invalid rule loader imported — only sis.rules.loader is allowed"


class SISScanner:
    def __init__(self, quiet=False, rules=None):
        self.quiet = quiet
        self.rules = rules
        self.parsers = {
            ".tf": "terraform",
            ".yaml": "kubernetes",
            ".yml": "kubernetes",
            "docker-compose.yml": "docker_compose",
            "docker-compose.yaml": "docker_compose",
            ".json": "cloudformation",
        }

    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan a single file and return findings"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine parser based on file extension/name
        file_type = self._get_file_type(str(path))

        if not file_type:
            print(f"⚠️  Unsupported file type: {file_path}")
            return []

        try:
            # Read file content
            with open(file_path, "r") as f:
                content = f.read()

            if not self.quiet: print(f"🔍 Scanning {file_path} as {file_type}")

            # Parse resources from file
            resources = parse_content(content, file_type)
            if not self.quiet: print(f"   Parsed {len(resources)} resources")

            # Normalize resource format for engine
            normalized_resources = []
            for resource in resources:
                # Convert 'kind' to 'type' if needed
                normalized = dict(resource)
                if "kind" in normalized and "type" not in normalized:
                    normalized["type"] = normalized["kind"]
                normalized_resources.append(normalized)

            # Load rules for this file type
            all_rules = self.rules if self.rules is not None else load_rules(["canonical"])
            file_rules = [
                r for r in all_rules if self._rule_applies_to_file(r, file_type)
            ]
            if not self.quiet: print(f"   Using {len(file_rules)} rules for {file_type}")

            # Validate resources against rules
            violations = validate_resources(normalized_resources, file_rules)
            if not self.quiet: print(f"   Found {len(violations)} violations")

            # Convert violations to findings format
            findings = []
            for violation in violations:
                finding = {
                    "file": file_path,
                    "rule_id": violation.get("rule_id", violation.get("id", "UNKNOWN")),
                    "severity": violation.get("severity", "MEDIUM").upper(),
                    "message": violation.get("message", ""),
                    "resource": violation.get("resource_id", "unknown"),
                    "resource_type": violation.get("resource_type", "unknown"),
                    "line": violation.get("location", {}).get("line", 0),
                    "remediation": violation.get("remediation", ""),
                    "_pack": violation.get("_pack", "N/A"),                    "_pack_version": violation.get("_pack_version", "N/A"),                }
                findings.append(finding)

            return findings

        except Exception as e:
            print(f"❌ Error scanning {file_path}: {e}")
            return []

    def scan_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Scan all supported files in a directory"""
        all_findings = []

        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)

                # Check if file is supported
                if self._get_file_type(file_path):
                    try:
                        findings = self.scan_file(file_path)
                        all_findings.extend(findings)
                    except Exception as e:
                        print(f"Error scanning {file_path}: {e}")

        return all_findings

    def _get_file_type(self, file_path: str) -> Optional[str]:
        """Get file type for parsing"""
        path = Path(file_path)
        filename = path.name.lower()

        # Check for docker-compose files first (by name)
        if "docker-compose" in filename:
            return "docker_compose"

        # Check by extension
        ext = path.suffix.lower()
        return self.parsers.get(ext)

    def _rule_applies_to_file(self, rule: Dict[str, Any], file_type: str) -> bool:
        """Check if a rule applies to a file type"""
        # Map file types to resource kinds
        type_to_kinds = {
            "terraform": [
                "aws_s3_bucket",
                "aws_iam_policy",
                "aws_security_group",
                "aws_iam_role",
                "aws_iam_user_policy",
                "aws_db_instance",
                "aws_vpc",
            ],
            "kubernetes": ["Pod", "Deployment", "StatefulSet", "DaemonSet"],
            "docker_compose": ["docker_service"],
            "cloudformation": ["AWS::S3::Bucket", "AWS::IAM::Policy"],
        }

        # Get resource kinds for this file type
        applicable_kinds = type_to_kinds.get(file_type, [])

        # Get resource kinds from rule
        rule_kinds = rule.get("applies_to", {}).get("resource_kinds", [])

        # If rule applies to all kinds or matches any of our kinds
        if "*" in rule_kinds or not rule_kinds:
            return True

        if any(kind in applicable_kinds for kind in rule_kinds):
            return True

        return False

# Alias for backward compatibility
Scanner = SISScanner
