"""
SIS Command Line Interface with Pack Support
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from .scanner import SISScanner
from .rules.loader import load_rules


def _print_monetization_info():
    """Print monetization information"""
    print("SIS - Security Inspection System")
    print("=" * 60)
    print("🚀 ENTERPRISE FEATURES & SERVICES AVAILABLE")
    print("=" * 60)
    print()
    print("✨ Premium Features:")
    print("  • GDPR/HIPAA/PCI-DSS Compliance Rules")
    print("  • Custom Rule Development")
    print("  • Priority Support & Training")
    print("  • Enterprise Deployment")
    print()
    print("💰 Pricing:")
    print("  • Custom Rules: $2,000 - $10,000 per set")
    print("  • Consulting: $200 - $500 per hour")
    print("  • Training: $3,000 per day")
    print()
    print("🎁 Special Offer:")
    print("  • First 10 customers: 50% OFF")
    print("  • Free security audit available")
    print()


def run_scan(args):
    """Run a security scan"""
    # Load rules from specified packs
    if hasattr(args, 'packs') and args.packs:
        rules = load_rules(args.packs)
    else:
        rules = load_rules(args.type)
    
    if not rules:
        print("❌ No rules found to scan with")
        return
    
    scanner = SISScanner(quiet=args.format == "json", rules=rules)
    
    target_path = Path(args.target)
    
    if not target_path.exists():
        print(f"❌ Target not found: {args.target}")
        return
    
    # Scan file or directory
    if target_path.is_file():
        findings = scanner.scan_file(str(target_path))
    else:
        findings = []
        for file_path in target_path.rglob("*"):
            if file_path.suffix in [".tf", ".yaml", ".yml", ".json"]:
                file_findings = scanner.scan_file(str(file_path))
                findings.extend(file_findings)
    
    # Output results
    if args.format == "json":
        output = json.dumps(findings, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)
    else:
        _print_text_results(findings, args.severity)
def _print_text_results(findings, severity_filter=None):
    """Print scan results in text format"""
    if severity_filter:
        severities = [s.upper() for s in severity_filter.split(",")]
        findings = [f for f in findings if f.get("severity") in severities]
    
    if not findings:
        print("✅ No security issues found!")
        return
    
    print(f"🔍 Found {len(findings)} security issue(s):")
    print("=" * 80)
    
    for i, finding in enumerate(findings, 1):
        print(f"\n{i}. {finding.get('rule_id', 'UNKNOWN')}")
        print(f"   Message: {finding.get('message', 'No message')}")
        print(f"   Severity: {finding.get('severity', 'UNKNOWN')}")
        print(f"   File: {finding.get('file', 'Unknown')}")
        print(f"   Line: {finding.get('line', 'Unknown')}")
        print(f"   Pack: {finding.get('_pack', 'N/A')} v{finding.get('_pack_version', 'N/A')}")


def list_rules(args):
    """List available security rules"""
    # Load rules from specified packs
    if hasattr(args, 'packs') and args.packs:
        rules = load_rules(args.packs)
    else:
        rules = load_rules(args.type)
    
    if not rules:
        print(f"No rules found")
        return
    
    print(f"📋 Available Rules:")
    print("=" * 80)
    
    for rule in rules:
        rule_id = rule.get("rule_id", rule.get("id", "UNKNOWN"))
        message = rule.get("message", rule.get("reason", "No description"))
        print(f"\n🔸 {rule_id}: {message}")
        print(f"   Type: {rule.get('rule_type', 'N/A')}")
        print(f"   Pack: {rule.get('_pack', 'N/A')} v{rule.get('_pack_version', 'N/A')}")
        if "remediation" in rule:
            print(f"   Fix: {rule['remediation']}")


def main():
    parser = argparse.ArgumentParser(
        description="SIS Security Scanner - Find security issues in infrastructure code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sis scan ./terraform/                    Scan all Terraform files in directory
  sis scan deployment.yaml                 Scan a Kubernetes file
  sis scan --format json ./infra/          Output as JSON
  sis scan --severity CRITICAL,HIGH        Only show critical/high issues
  sis scan --output report.json ./src/     Save results to file
  sis scan --packs canonical ./infra/      Use specific rule packs
  sis rules --packs canonical              List rules from specific packs
        
Supported file types:
  • Terraform (.tf)
  • Kubernetes (.yaml, .yml)
  • Docker Compose (docker-compose.yml)
  • CloudFormation (.json, .yaml, .yml)
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan files or directories")
    scan_parser.add_argument(
        "target",
        help="File or directory to scan"
    )
    scan_parser.add_argument(
        "--type",
        default="all",
        help="Rule type filter (default: all)",
    )
    scan_parser.add_argument(
        "--packs",
        nargs="+",
        help="Rule packs to load (e.g., canonical defi-irreversibility)",
    )
    scan_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    scan_parser.add_argument(
        "--severity",
        help="Comma-separated severity filter (e.g., CRITICAL,HIGH)",
    )
    scan_parser.add_argument(
        "--output",
        help="Output file (for JSON format)",
    )
    scan_parser.set_defaults(func=run_scan)
    
    # Rules command
    rules_parser = subparsers.add_parser("rules", help="List available security rules")
    rules_parser.add_argument(
        "--type",
        default="all",
        help="Rule type filter (default: all)",
    )
    rules_parser.add_argument(
        "--packs",
        nargs="+",
        help="Rule packs to list (e.g., canonical defi-irreversibility)",
    )
    rules_parser.set_defaults(func=list_rules)
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command is None:
        _print_monetization_info()
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
