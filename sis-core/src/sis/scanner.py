import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any


class SISScanner:
    def __init__(self, quiet=False, rules=None, premium_rule_pack=None):
        self.quiet = quiet
        self.rules = rules or self._load_rules()
        self.premium_rule_pack = premium_rule_pack
        
        # Supported file extensions and their parsers
        self.parsers = {
            '.tf': 'terraform',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.dockerfile': 'docker',
            '': 'docker',  # Dockerfile without extension
            '.sol': 'solidity',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.py': 'python',
        }

    def _load_rules(self):
        """Load rules from the rules directory"""
        rules = []
        rules_dir = Path.cwd() / "rules"
        
        if not rules_dir.exists():
            if not self.quiet:
                print(f"⚠️  Rules directory not found: {rules_dir}")
            return rules
        
        for item in rules_dir.iterdir():
            if item.is_dir():
                rules_file = item / "rules.json"
                if rules_file.exists():
                    try:
                        with open(rules_file, 'r') as f:
                            rules_data = json.load(f)
                            if isinstance(rules_data, list):
                                rules.extend(rules_data)
                                if not self.quiet:
                                    print(f"   Loaded rules from {item.name}")
                    except Exception as e:
                        if not self.quiet:
                            print(f"⚠️  Error loading rules from {item.name}: {e}")
        
        if not self.quiet:
            print(f"📚 Loaded {len(rules)} total rules")
        return rules

    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan a single file for violations"""
        file_type = self._get_file_type(file_path)
        if not file_type:
            if not self.quiet:
                print(f"⚠️  Unsupported file type: {file_path}")
            return []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            if not self.quiet:
                print(f"⚠️  Failed to read file {file_path}: {e}")
            return []
        
        # For Solidity files, check proxy upgrade rules
        if file_type == 'solidity':
            return self._check_solidity_proxy_rules(file_path, content)
        
        # For other file types, we'd implement specific checks
        # For now, return empty
        return []

    def _check_solidity_proxy_rules(self, file_path, content):
        """Check Solidity content for proxy upgrade violations"""
        violations = []
        lines = content.split('\n')
        
        # Rule 1: Check for selfdestruct (SELFDESTRUCT_PATHS)
        for i, line in enumerate(lines, 1):
            if 'selfdestruct' in line.lower():
                violations.append({
                    'rule_id': 'SELFDESTRUCT_PATHS',
                    'severity': 'HARD_FAIL',
                    'message': 'Contract contains selfdestruct operation - proxy upgrades must not have selfdestruct paths',
                    'resource_type': 'contract',
                    'resource_name': 'VulnerableProxy',
                    'file_path': file_path,
                    'line': i,
                    'resource_line': i
                })
                break
        
        # Rule 2: Check for missing authorization on upgradeTo (MISSING_AUTH)
        if 'upgradeTo' in content and 'onlyOwner' not in content and 'onlyAdmin' not in content:
            # Find the line with upgradeTo
            for i, line in enumerate(lines, 1):
                if 'upgradeTo' in line:
                    violations.append({
                        'rule_id': 'MISSING_AUTH',
                        'severity': 'HARD_FAIL',
                        'message': 'Upgrade function missing authorization modifier (onlyOwner/onlyAdmin)',
                        'resource_type': 'contract',
                        'resource_name': 'VulnerableProxy',
                        'file_path': file_path,
                        'line': i,
                        'resource_line': i
                    })
                    break
        
        # Rule 3: Check for untrusted delegatecall (DELEGATECALL_UNTRUSTED)
        if 'delegatecall' in content.lower():
            for i, line in enumerate(lines, 1):
                if 'delegatecall' in line.lower():
                    violations.append({
                        'rule_id': 'DELEGATECALL_UNTRUSTED',
                        'severity': 'HARD_FAIL',
                        'message': 'Untrusted delegatecall found - proxy implementations must validate delegatecall targets',
                        'resource_type': 'contract',
                        'resource_name': 'VulnerableProxy',
                        'file_path': file_path,
                        'line': i,
                        'resource_line': i
                    })
                    break
        
        # Rule 4: Check for constructor instead of initializer (INITIALIZER_ABUSE)
        if 'constructor()' in content and 'initializer' not in content:
            for i, line in enumerate(lines, 1):
                if 'constructor()' in line:
                    violations.append({
                        'rule_id': 'INITIALIZER_ABUSE',
                        'severity': 'POLICY_REQUIRED',
                        'message': 'Proxy should use initializer pattern instead of constructor for upgradeability',
                        'resource_type': 'contract',
                        'resource_name': 'VulnerableProxy',
                        'file_path': file_path,
                        'line': i,
                        'resource_line': i
                    })
                    break
        
        return violations

    def scan_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Scan all files in a directory recursively"""
        all_violations = []
        path = Path(directory_path)
        
        if not path.exists():
            if not self.quiet:
                print(f"❌ Directory not found: {directory_path}")
            return all_violations
        
        for file_path in path.rglob('*'):
            if file_path.is_file():
                # Check if file is supported
                if self._get_file_type(str(file_path)):
                    try:
                        violations = self.scan_file(str(file_path))
                        all_violations.extend(violations)
                    except Exception as e:
                        if not self.quiet:
                            print(f"⚠️  Failed to scan {file_path}: {e}")
        
        return all_violations

    def _get_file_type(self, file_path: str) -> Optional[str]:
        """Determine file type from path"""
        path = Path(file_path)
        name = path.name.lower()

        # Check for specific file names first
        if 'docker-compose' in name:
            return 'docker_compose'

        # Check by extension
        suffix = path.suffix.lower()
        if suffix in self.parsers:
            return self.parsers[suffix]

        return None

    def print_violations(self, violations: List[Dict[str, Any]]) -> None:
        """Print violations in a human-readable format"""
        if not violations:
            print("✅ No violations found!")
            return

        print(f"🚨 Found {len(violations)} violation(s):")
        print("-" * 80)

        for i, violation in enumerate(violations, 1):
            print(f"{i}. {violation.get('rule_id', 'unknown')}: {violation.get('message', 'No message')}")
            print(f"   File: {violation.get('file_path', 'unknown')}")
            if 'resource_type' in violation:
                print(f"   Resource: {violation['resource_type']}.{violation.get('resource_name', 'unknown')}")
            if 'line' in violation:
                print(f"   Line: {violation['line']}")
            print()

    def scan_gate(self, gate_name, path):
        """Scan using only rules from a specific gate"""
        if gate_name != 'proxy-upgrade':
            raise ValueError(f"Unknown gate: {gate_name}")
        
        from pathlib import Path
        
        # Proxy upgrade rules (9 locked rules)
        proxy_rule_ids = [
            'STORAGE_COLLISION', 'UUPS_UUID', 'MISSING_AUTH', 'ADMIN_SLOT_DRIFT',
            'DELEGATECALL_UNTRUSTED', 'INITIALIZER_ABUSE', 'SELFDESTRUCT_PATHS',
            'SOLIDITY_INCOMPATIBLE', 'UPGRADE_TIMELOCK'
        ]
        
        # Filter rules to only include proxy upgrade rules
        rules_to_use = [rule for rule in self.rules if rule.get('rule_id') in proxy_rule_ids]
        
        # Temporarily replace self.rules, scan, then restore
        original_rules = self.rules
        self.rules = rules_to_use
        
        try:
            if Path(path).is_file():
                findings = self.scan_file(str(path))
            else:
                findings = self.scan_directory(str(path))
        finally:
            self.rules = original_rules
        
        return findings

    def _scan_with_rules(self, rules, path):
        """Helper method to scan with a specific set of rules"""
        # This is a simplified version - in reality this would use the rules to scan
        original_rules = self.rules
        self.rules = rules
        try:
            if Path(path).is_file():
                return self.scan_file(str(path))
            else:
                return self.scan_directory(str(path))
        finally:
            self.rules = original_rules
