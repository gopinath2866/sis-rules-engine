"""
SIS Unified Scanner - Main scanning orchestration
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from .parsers import terraform, kubernetes, docker_compose, cloudformation, arm

class SISScanner:
    def __init__(self):
        self.parsers = {
            '.tf': terraform.parse_terraform,
            '.yaml': kubernetes.parse_kubernetes,
            '.yml': kubernetes.parse_kubernetes,
            'docker-compose.yml': docker_compose.parse_docker_compose,
            'docker-compose.yaml': docker_compose.parse_docker_compose,
            '.json': cloudformation.parse_cloudformation,  # CloudFormation JSON
        }
        
    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan a single file and return findings"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine parser based on file extension/name
        parser = self._get_parser_for_file(str(path))
        
        if not parser:
            return []
        
        try:
            # Read file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse resources from file
            resources = parser(content, file_format=path.suffix)
            
            # Validate resources against rules (using your engine)
            from .engine import validate_resources
            from .rules import load_rules  # We'll create this
            
            # Load appropriate rules for file type
            rules = load_rules(file_type=self._get_file_type(str(path)))
            
            # Validate
            violations = validate_resources(resources, rules)
            
            # Format findings with file context
            findings = []
            for violation in violations:
                finding = {
                    'file': file_path,
                    'rule_id': violation.get('rule_id'),
                    'severity': violation.get('severity', 'MEDIUM'),
                    'message': violation.get('message'),
                    'resource': violation.get('resource_id'),
                    'resource_type': violation.get('resource_type'),
                    'line': violation.get('location', {}).get('line', 0),
                    'remediation': violation.get('remediation', ''),
                }
                findings.append(finding)
            
            return findings
            
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            return []
    
    def scan_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Scan all supported files in a directory"""
        all_findings = []
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check if file is supported
                if self._get_parser_for_file(file_path):
                    try:
                        findings = self.scan_file(file_path)
                        all_findings.extend(findings)
                    except Exception as e:
                        print(f"Error scanning {file_path}: {e}")
        
        return all_findings
    
    def _get_parser_for_file(self, file_path: str) -> Optional[callable]:
        """Get appropriate parser for file"""
        path = Path(file_path)
        filename = path.name.lower()
        
        # Check for docker-compose files first (by name)
        if 'docker-compose' in filename:
            return self.parsers.get('docker-compose.yml')
        
        # Check by extension
        ext = path.suffix.lower()
        return self.parsers.get(ext)
    
    def _get_file_type(self, file_path: str) -> str:
        """Get file type for rule loading"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        mapping = {
            '.tf': 'terraform',
            '.yaml': 'kubernetes',
            '.yml': 'kubernetes',
            'docker-compose.yml': 'docker',
            'docker-compose.yaml': 'docker',
            '.json': 'cloudformation',
        }
        
        # Check for docker-compose first
        if 'docker-compose' in path.name.lower():
            return 'docker'
        
        return mapping.get(ext, 'unknown')
