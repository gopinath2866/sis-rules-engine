"""
SIS CLI - Minimal, stable interface.
No f-string multiline. No generation. No cleverness.
"""
import argparse
import json
import sys
from pathlib import Path

# Direct imports - no dynamic paths
try:
    from .scanner import Scanner
    from .rules import load_rules
except ImportError:
    # Fallback for direct execution
    from scanner import Scanner
    from rules import load_rules

def run_scan(args):
    """Scan Terraform files for irreversible patterns."""
    scanner = Scanner()
    rules = load_rules()
    
    all_findings = []
    
    for file_path in args.files:
        if not Path(file_path).exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            continue
            
        try:
            findings = scanner.scan(file_path, rules)
            all_findings.extend(findings)
        except Exception as e:
            print(f"Error scanning {file_path}: {e}", file=sys.stderr)
            continue
    
    # Output formatting
    if args.format == 'json':
        output = format_json_output(all_findings, len(args.files))
        print(json.dumps(output, indent=2))
    else:
        format_text_output(all_findings)
    
    return 1 if all_findings else 0

def format_json_output(findings, files_scanned):
    """Format findings as structured JSON."""
    if findings:
        violations = []
        for f in findings:
            violations.append({
                "rule_id": f.get("rule_id", "UNKNOWN"),
                "message": f.get("message", ""),
                "severity": f.get("severity", "MEDIUM"),
                "file": f.get("file_path", ""),
                "resource": {
                    "type": f.get("resource_type", ""),
                    "name": f.get("resource_name", "")
                },
                "line": f.get("line", 1)
            })
        
        return {
            "summary": {
                "total_violations": len(findings),
                "rules_fired": sorted(list(set([v["rule_id"] for v in findings if v.get("rule_id")]))),
                "files_scanned": files_scanned
            },
            "violations": violations
        }
    else:
        return {
            "summary": {
                "total_violations": 0,
                "rules_fired": [],
                "files_scanned": files_scanned
            },
            "violations": []
        }

def format_text_output(findings):
    """Format findings as human-readable text."""
    if not findings:
        print("✅ No violations found.")
        return
    
    # Group by file
    by_file = {}
    for finding in findings:
        file_path = finding.get("file_path", "unknown")
        by_file.setdefault(file_path, []).append(finding)
    
    for file_path, file_findings in by_file.items():
        print(f"\n{file_path}:")
        for finding in file_findings:
            rule_id = finding.get("rule_id", "UNKNOWN")
            message = finding.get("message", "")
            print(f"  ❌ {rule_id}: {message}")



def run_explain(args):
    """Explain a specific rule."""
    import sys, json
    from sis.rules import load_rules

    try:
        rules = load_rules()
    except Exception as e:
        print(f"Error loading rules: {e}", file=sys.stderr)
        return 1

    found_rule = None
    for rule in rules:
        if isinstance(rule, dict) and rule.get("rule_id") == args.rule_id:
            found_rule = rule
            break

    if not found_rule:
        print(f"Rule '{args.rule_id}' not found.", file=sys.stderr)
        available = [r.get("rule_id") for r in rules if isinstance(r, dict) and r.get("rule_id")]
        if available:
            print(f"Available rules: {available[:5]}", file=sys.stderr)
        return 1

    if hasattr(args, "format") and args.format == "json":
        print(json.dumps(found_rule, indent=2))
    else:
        rule_id = found_rule.get("rule_id", "UNKNOWN")
        rule_type = found_rule.get("rule_type", "Unknown")
        message = found_rule.get("message", "No message")
        print(f"Rule: {rule_id}")
        print(f"Type: {rule_type}")
        print(f"Message: {message}")

        detection = found_rule.get("detection", {})
        if detection:
            match_logic = detection.get("match_logic", "UNKNOWN")
            conditions = detection.get("conditions", [])
            print(f"Detection logic: {match_logic}")
            if conditions:
                print("Conditions:")
                for i, cond in enumerate(conditions, 1):
                    path = cond.get("path", "unknown")
                    operator = cond.get("operator", "unknown")
                    value = cond.get("value", "unknown")
                    print(f"  {i}. path={path}, operator={operator}, value={value}")
    return 0

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='SIS: Static Irreversibility Scanner',
        prog='sis-scan'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan Terraform files')
    scan_parser.add_argument('files', nargs='+', help='Terraform files to scan')
    scan_parser.add_argument('--format', choices=['text', 'json'], 
                           default='text', help='Output format')
    scan_parser.set_defaults(func=run_scan)
    
    # Explain command
    explain_parser = subparsers.add_parser('explain', help='Explain a rule')
    explain_parser.add_argument('rule_id', help='Rule ID to explain')
    explain_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    explain_parser.set_defaults(func=run_explain)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
