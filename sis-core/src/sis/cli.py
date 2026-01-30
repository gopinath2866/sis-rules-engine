#!/usr/bin/env python3
"""
CLI entry point for SIS (Security Invariant Scanner)
"""

import sys
import json
import argparse

try:
    from .scanner import Scanner
    SCANNER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Scanner import warning: {e}")
    SCANNER_AVAILABLE = False

# Define load_rules function here to avoid import issues
def load_rules():
    """Load rules with fallback to default."""
    try:
        from .rules import load_rules as load_rules_from_module
        return load_rules_from_module()
    except ImportError:
        # Fallback to default rule
        return [{
            'id': 'proxy-admin-not-zero-address',
            'title': 'Proxy admin must not be the zero address',
            'description': 'The admin of a proxy should be a valid address, not 0x0',
            'severity': 'high',
            'gate': 'proxy-upgrade'
        }]

from .exception_handler import ExceptionHandler
from .provenance_emitter import ProvenanceEmitter

def load_rules():
    """Load all rules from the rules directory"""
    rules = []
    # This is a stub - in a real implementation, rules would be loaded from files
    rules.append({
        'id': 'proxy-admin-not-zero-address',
        'title': 'Proxy admin must not be the zero address',
        'description': 'The admin of a proxy should be a valid address, not 0x0',
        'severity': 'high',
        'gate': 'proxy-upgrade'
    })
    return rules

def run_scan(args):
    """Run a scan against the target directory or file"""
    
    if not SCANNER_AVAILABLE:
        print("❌ Scanner module not available", file=sys.stderr)
        return 1
    
    scanner = Scanner()
    rules = load_rules()
    
    # If a specific gate is provided, filter rules
    if hasattr(args, 'gate') and args.gate:
        rules = [r for r in rules if r.get('gate') == args.gate]
        if not rules:
            print(f"❌ No rules found for gate: {args.gate}", file=sys.stderr)
            return 1
    
    # Run the scan
    findings = scanner.scan(args.target, rules)
    
    # Filter to only blocking findings
    blocking_findings = [f for f in findings if f.get('severity') in ['high', 'critical']]
    
    # Initialize output data
    output_data = {
        "findings": findings,
        "blocking_findings": blocking_findings,
        "summary": {
            "total": len(findings),
            "blocking": len(blocking_findings)
        }
    }
    
    # Gate-specific scan output
    if hasattr(args, 'gate') and args.gate:
        if blocking_findings:
            if not args.quiet and not args.output:
                for finding in blocking_findings:
                    print(f"❌ {finding['rule_id']}: {finding['description']}")
                print(f"\n🚫 {len(blocking_findings)} blocking violation(s) found in gate '{args.gate}'")
            if args.output or args.format == 'json':
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(output_data, f, indent=2)
                else:
                    print(json.dumps(output_data, indent=2))
        else:
            if not args.quiet and not args.output:
                print(f"✅ No blocking violations found in gate '{args.gate}'")
        
        # Exception handling (governance acknowledgement) - GATE SCANS
        if hasattr(args, 'acknowledge_exception') and args.acknowledge_exception and findings:
            try:
                exception_data = ExceptionHandler.validate_exception(
                    args.acknowledge_exception,
                    args.gate,
                    findings
                )
                
                if exception_data:
                    # If public key is provided, verify the signature
                    if args.public_key:
                        try:
                            from .signing import verify_exception
                            with open(args.public_key, 'r') as f:
                                public_key_pem = f.read()
                            if not verify_exception(exception_data, public_key_pem):
                                print(f"⚠️  Exception artifact ignored (signature verification failed)", file=sys.stderr)
                                exception_data = None
                        except Exception as e:
                            print(f"⚠️  Exception artifact ignored (signature verification error: {e})", file=sys.stderr)
                            exception_data = None
                    
                    if exception_data:
                        cli_output, json_output = ExceptionHandler.get_governance_output(exception_data)
                        if not args.quiet and not args.output:
                            print(cli_output)
                        
                        # Add to JSON output if we're outputting JSON
                        if args.output or args.format == 'json':
                            output_data["governance"] = json_output
                            if args.output:
                                with open(args.output, 'w') as f:
                                    json.dump(output_data, f, indent=2)
            except Exception as e:
                # Invalid exceptions are silently ignored (just log to stderr)
                print(f"⚠️  Exception artifact ignored: {e}", file=sys.stderr)
        
        return 1 if blocking_findings else 0
    
    # Original scan logic (if no gate specified)
    all_findings = findings
    
    if all_findings:
        if not args.quiet and not args.output:
            for finding in all_findings:
                severity = finding.get('severity', 'medium')
                severity_icon = '❌' if severity in ['high', 'critical'] else '⚠️'
                print(f"{severity_icon} [{severity.upper()}] {finding['rule_id']}: {finding['description']}")
            print(f"\n📊 Found {len(all_findings)} total violation(s)")
        
        if args.output or args.format == 'json':
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=2)
            else:
                print(json.dumps(output_data, indent=2))
    else:
        if not args.quiet and not args.output:
            print("✅ No violations found.")
    
    # Exception handling for non-gate scans
    if hasattr(args, 'acknowledge_exception') and args.acknowledge_exception and all_findings:
        try:
            exception_data = ExceptionHandler.validate_exception(
                args.acknowledge_exception,
                args.gate if hasattr(args, 'gate') and args.gate else 'full-scan',
                all_findings
            )
            
            if exception_data:
                # If public key is provided, verify the signature
                # Emit provenance (fire-and-forget, constitutional vent)
                try:
                    context_id = ProvenanceEmitter.create_execution_context()
                    ProvenanceEmitter.emit_exception_provenance(
                        exception_data=exception_data,
                        verification_result=True,
                        public_key_fingerprint=args.public_key,
                        execution_context=context_id
                    )
                except Exception:
                    # Constitutional: Provenance emission failures are non-events
                    pass
                
                # Emit provenance (fire-and-forget, constitutional vent)
                try:
                    context_id = ProvenanceEmitter.create_execution_context()
                    ProvenanceEmitter.emit_exception_provenance(
                        exception_data=exception_data,
                        verification_result=True,
                        public_key_fingerprint=args.public_key,
                        execution_context=context_id
                    )
                except Exception:
                    # Constitutional: Provenance emission failures are non-events
                    pass
                
                if args.public_key:
                    try:
                        from .signing import verify_exception
                        with open(args.public_key, 'r') as f:
                            public_key_pem = f.read()
                        if not verify_exception(exception_data, public_key_pem):
                            print(f"⚠️  Exception artifact ignored (signature verification failed)", file=sys.stderr)
                            exception_data = None
                    except Exception as e:
                        print(f"⚠️  Exception artifact ignored (signature verification error: {e})", file=sys.stderr)
                        exception_data = None
                
                if exception_data:
                    cli_output, json_output = ExceptionHandler.get_governance_output(exception_data)
                    if not args.quiet and not args.output:
                        print(cli_output)
                    
                    # Add to JSON output if we're outputting JSON
                    if args.output or args.format == 'json':
                        output_data["governance"] = json_output
                        if args.output:
                            with open(args.output, 'w') as f:
                                json.dump(output_data, f, indent=2)
        except Exception as e:
            # Invalid exceptions are silently ignored (just log to stderr)
            print(f"⚠️  Exception artifact ignored: {e}", file=sys.stderr)
    
    return 0 if len(all_findings) == 0 else 1

def run_explain(args):
    """Explain a specific rule"""
    rules = load_rules()
    rule = next((r for r in rules if r['id'] == args.rule_id), None)
    
    if rule:
        print(f"Rule: {rule['id']}")
        print(f"Title: {rule['title']}")
        print(f"Description: {rule['description']}")
        print(f"Severity: {rule['severity']}")
        if 'gate' in rule:
            print(f"Gate: {rule['gate']}")
    else:
        print(f"Rule '{args.rule_id}' not found", file=sys.stderr)
        return 1
    return 0

def main():
    parser = argparse.ArgumentParser(description='Security Invariant Scanner')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for violations')
    scan_parser.add_argument('target', help='Target directory or file to scan')
    scan_parser.add_argument('--gate', 
                           help='Only run rules for a specific gate',
                           choices=['proxy-upgrade'])
    scan_parser.add_argument('--format',
                           help='Output format',
                           choices=['text', 'json'],
                           default='text')
    scan_parser.add_argument('--output', '-o',
                           help='Output file (default: stdout)')
    scan_parser.add_argument('--quiet', '-q',
                           action='store_true',
                           help='Suppress output to stdout')
    scan_parser.add_argument('--premium-rule-pack',
                           help='Path to premium rule pack (Pro/Enterprise only)')
    scan_parser.add_argument('--acknowledge-exception',
                           help='Path to governance exception artifact (acknowledgement only)',
                           type=str, default=None)
    scan_parser.add_argument('--public-key',
                           help='Path to public key for signature verification',
                           type=str, default=None)
    
    # Explain command
    explain_parser = subparsers.add_parser('explain', help='Explain a rule')
    explain_parser.add_argument('rule_id', help='Rule ID to explain')
    
    args = parser.parse_args()
    
    if args.command == 'scan':
        sys.exit(run_scan(args))
    elif args.command == 'explain':
        sys.exit(run_explain(args))
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
