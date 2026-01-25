"""
SIS Command Line Interface
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from .scanner import SISScanner


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
    scan_parser.add_argument("path", help="File or directory to scan")
    scan_parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json", "sarif", "html"],
        default="text",
        help="Output format (default: text)",
    )
    scan_parser.add_argument(
        "--severity",
        "-s",
        help="Filter by severity (comma-separated: CRITICAL,HIGH,MEDIUM,LOW)",
    )
    scan_parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    scan_parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress progress output"
    )

    # List rules command
    rules_parser = subparsers.add_parser("rules", help="List available security rules")
    rules_parser.add_argument(
        "--type",
        "-t",
        choices=["terraform", "kubernetes", "docker", "cloudformation", "all"],
        default="all",
        help="Filter rules by type",
    )

    # Version command
    subparsers.add_parser("version", help="Show version information")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "scan":
        run_scan(args)
    elif args.command == "rules":
        list_rules(args)
    elif args.command == "version":
        print_version()


def run_scan(args):
    """Run security scan"""
    scanner = SISScanner()
    path = Path(args.path)

    if not path.exists():
        print(f"❌ Error: Path does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)

    if not args.quiet:
        print(f"🔍 Scanning: {args.path}")

    # Perform scan
    if path.is_file():
        findings = scanner.scan_file(str(path))
    else:
        findings = scanner.scan_directory(str(path))

    # Filter by severity if specified
    if args.severity:
        severities = [s.strip().upper() for s in args.severity.split(",")]
        findings = [f for f in findings if f.get("severity") in severities]

    # Generate output
    output = generate_output(findings, args.format, args.path)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        if not args.quiet:
            print(f"📄 Report written to: {args.output}")
    else:
        print(output)


def list_rules(args):
    """List available security rules"""
    from .rules import load_rules

    rules = load_rules(args.type)

    if not rules:
        print(f"No rules found for type: {args.type}")
        return

    print(f"📋 Available Rules ({args.type}):")
    print("=" * 80)

    for rule in rules:
        print(f"\n🔸 {rule['rule_id']}: {rule['message']}")
        print(f"   Severity: {rule['severity']}")
        print(f"   Applies to: {', '.join(rule['applies_to']['resource_kinds'])}")
        print(f"   Type: {rule['rule_type']}")
        if "remediation" in rule:
            print(f"   Fix: {rule['remediation']}")


def print_version():
    """Print version information"""
    version = "1.0.0"
    print(f"SIS Security Scanner v{version}")
    print("Security scanning for infrastructure-as-code")
    print("https://github.com/yourusername/sis")


def generate_output(findings: List[Dict[str, Any]], format: str, scan_path: str) -> str:
    """Generate output in specified format"""
    if format == "json":
        return generate_json(findings, scan_path)
    elif format == "sarif":
        return generate_sarif(findings, scan_path)
    elif format == "html":
        return generate_html(findings, scan_path)
    else:  # text format (default)
        return generate_text_report(findings, scan_path)


def generate_json(findings: List[Dict[str, Any]], scan_path: str) -> str:
    """Generate JSON output"""
    from datetime import datetime

    # Count by severity
    by_severity = {}
    for finding in findings:
        severity = finding.get("severity", "UNKNOWN")
        by_severity[severity] = by_severity.get(severity, 0) + 1

    result = {
        "scan": {
            "path": scan_path,
            "timestamp": datetime.now().isoformat(),
            "findings_count": len(findings),
        },
        "findings": findings,
        "summary": {"total": len(findings), "by_severity": by_severity},
    }

    # Use default=str to handle any non-serializable objects
    return json.dumps(result, indent=2, default=str)


def generate_text_report(findings: List[Dict[str, Any]], scan_path: str) -> str:
    """Generate human-readable text report"""
    if not findings:
        return "✅ No security issues found!\n"

    # Group by severity
    by_severity = {}
    for finding in findings:
        severity = finding.get("severity", "UNKNOWN")
        by_severity.setdefault(severity, []).append(finding)

    # Generate report
    report = []
    report.append("=" * 80)
    report.append("🔒 SIS Security Scan Report")
    report.append("=" * 80)
    report.append(f"📁 Scan Path: {scan_path}")
    report.append(f"📅 Generated: {get_current_time()}")
    report.append(f"📊 Total Issues: {len(findings)}")
    report.append("")

    # Severity summary
    severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    report.append("📈 SEVERITY SUMMARY:")
    for severity in severity_order:
        if severity in by_severity:
            count = len(by_severity[severity])
            icon = get_severity_icon(severity)
            report.append(f"  {icon} {severity}: {count}")

    report.append("")
    report.append("=" * 80)

    # Detailed findings by severity
    for severity in severity_order:
        if severity in by_severity:
            icon = get_severity_icon(severity)
            report.append(
                f"\n{icon} {severity.upper()} SEVERITY ({len(by_severity[severity])}):"
            )
            report.append("-" * 40)

            for finding in by_severity[severity]:
                rule_id = finding.get("rule_id", "UNKNOWN")
                resource = finding.get("resource", "unknown")
                message = finding.get("message", "")
                file_path = finding.get("file", "")
                line = finding.get("line", "")

                report.append(f"\n🔸 {rule_id}: {resource}")
                report.append(f"   📝 {message}")

                location = f"   📍 {file_path}"
                if line:
                    location += f":{line}"
                report.append(location)

                remediation = finding.get("remediation", "")
                if remediation:
                    report.append(f"   💡 {remediation}")

    report.append("")
    report.append("=" * 80)
    report.append("📋 RECOMMENDATIONS:")
    report.append("1. Fix CRITICAL issues immediately")
    report.append("2. Review HIGH issues within 7 days")
    report.append("3. Address MEDIUM/LOW issues in next sprint")
    report.append("")
    report.append("🏁 Scan complete!")

    return "\n".join(report)


def generate_sarif(findings: List[Dict[str, Any]], scan_path: str) -> str:
    """Generate SARIF format for CI/CD integration"""
    from datetime import datetime

    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "SIS Security Scanner",
                        "informationUri": "https://github.com/yourusername/sis",
                        "version": "1.0.0",
                        "rules": [],
                    }
                },
                "results": [],
            }
        ],
    }

    # Convert findings to SARIF results
    for finding in findings:
        result = {
            "ruleId": finding.get("rule_id", "UNKNOWN"),
            "level": severity_to_sarif_level(finding.get("severity", "MEDIUM")),
            "message": {"text": finding.get("message", "Security issue found")},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": finding.get("file", "").replace(str(scan_path), "")
                        }
                    }
                }
            ],
        }
        sarif["runs"][0]["results"].append(result)

    return json.dumps(sarif, indent=2)


def generate_html(findings: List[Dict[str, Any]], scan_path: str) -> str:
    """Generate HTML report"""
    from datetime import datetime

    # Simple HTML report
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>SIS Security Report - {scan_path}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .critical {{ color: #d32f2f; font-weight: bold; }}
        .high {{ color: #f57c00; }}
        .medium {{ color: #fbc02d; }}
        .low {{ color: #388e3c; }}
        .finding {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .severity-badge {{ padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; }}
        .critical-badge {{ background: #d32f2f; color: white; }}
        .high-badge {{ background: #f57c00; color: white; }}
        .medium-badge {{ background: #fbc02d; color: black; }}
        .low-badge {{ background: #388e3c; color: white; }}
    </style>
</head>
<body>
    <h1>🔒 SIS Security Scan Report</h1>
    
    <div class="summary">
        <h3>Scan Summary</h3>
        <p><strong>Path:</strong> {scan_path}</p>
        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Total Issues:</strong> {len(findings)}</p>
    </div>
    
    <h2>Findings</h2>
    {generate_findings_html(findings)}
    
    <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd;">
        <p>Generated by SIS Security Scanner v1.0.0</p>
        <p><a href="https://github.com/yourusername/sis">https://github.com/yourusername/sis</a></p>
    </footer>
</body>
</html>"""
    return html


def generate_findings_html(findings: List[Dict[str, Any]]) -> str:
    """Generate HTML for findings"""
    if not findings:
        return "<p>✅ No security issues found!</p>"

    html_parts = []
    for finding in findings:
        severity = finding.get("severity", "UNKNOWN")
        severity_class = severity.lower()
        badge_class = f"{severity_class}-badge"

        html = f"""
        <div class="finding {severity_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0;">{finding.get('rule_id')}: {finding.get('resource')}</h3>
                <span class="severity-badge {badge_class}">{severity}</span>
            </div>
            <p><strong>File:</strong> {finding.get('file')}:{finding.get('line')}</p>
            <p><strong>Issue:</strong> {finding.get('message')}</p>
            <p><strong>Fix:</strong> {finding.get('remediation')}</p>
        </div>
        """
        html_parts.append(html)

    return "\n".join(html_parts)


def get_severity_icon(severity: str) -> str:
    """Get icon for severity level"""
    icons = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🟢",
        "UNKNOWN": "⚪",
    }
    return icons.get(severity, "⚪")


def severity_to_sarif_level(severity: str) -> str:
    """Convert SIS severity to SARIF level"""
    mapping = {"CRITICAL": "error", "HIGH": "error", "MEDIUM": "warning", "LOW": "note"}
    return mapping.get(severity, "warning")


def get_current_time() -> str:
    """Get current time in readable format"""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    main()
