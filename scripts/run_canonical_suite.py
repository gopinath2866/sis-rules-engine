#!/usr/bin/env python3
"""
Run the canonical test suite and produce a summary
"""
import subprocess
import json
import sys
import os
from pathlib import Path
import xml.etree.ElementTree as ET

def run_canonical_suite():
    """Execute the canonical test suite"""
    print("🚀 Running SIS v1.0.0 Canonical Test Suite...")
    print("=" * 60)
    
    # Create test-results directory
    Path("test-results").mkdir(exist_ok=True)
    
    try:
        # Try with json-report plugin
        result = subprocess.run([
            "pytest", "tests/",
            "-v",
            "--tb=short",
            "--junitxml=test-results/canonical.xml",
            "--json-report",
            "--json-report-file=test-results/report.json"
        ], capture_output=True, text=True)
    except:
        # Fallback without json-report
        result = subprocess.run([
            "pytest", "tests/",
            "-v",
            "--tb=short",
            "--junitxml=test-results/canonical.xml"
        ], capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    # Try to load JSON report first
    report_path = Path("test-results/report.json")
    if report_path.exists():
        try:
            with open(report_path) as f:
                report = json.load(f)
            
            summary = report.get("summary", {})
            print_summary(summary)
            return summary.get('failed', 0) == 0
        except json.JSONDecodeError:
            print("⚠️  JSON report is corrupted, trying XML...")
    
    # Fallback to JUnit XML parsing
    xml_path = Path("test-results/canonical.xml")
    if xml_path.exists():
        try:
            summary = parse_junit_xml(xml_path)
            print_summary(summary)
            return summary.get('failed', 0) == 0
        except ET.ParseError:
            print("⚠️  XML report is corrupted")
    
    # Last resort: parse stdout
    summary = parse_stdout(result.stdout)
    print_summary(summary)
    return summary.get('failed', 0) == 0

def parse_junit_xml(xml_path):
    """Parse JUnit XML results"""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    summary = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'duration': 0.0
    }
    
    # Look for testsuite elements
    for testsuite in root.findall('.//testsuite'):
        summary['total'] += int(testsuite.get('tests', 0))
        summary['passed'] += int(testsuite.get('tests', 0)) - int(testsuite.get('failures', 0)) - int(testsuite.get('errors', 0))
        summary['failed'] += int(testsuite.get('failures', 0)) + int(testsuite.get('errors', 0))
        summary['skipped'] += int(testsuite.get('skipped', 0))
        summary['duration'] += float(testsuite.get('time', 0))
    
    return summary

def parse_stdout(stdout):
    """Parse pytest stdout for summary"""
    lines = stdout.strip().split('\n')
    summary = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'duration': 0.0
    }
    
    for line in reversed(lines):
        if line.startswith('====='):
            continue
        if 'passed' in line and 'failed' in line:
            # Parse line like: "4 passed in 0.08s" or "3 passed, 1 failed in 0.1s"
            parts = line.split()
            for part in parts:
                if part.endswith('passed'):
                    summary['passed'] = int(part.replace('passed', ''))
                elif part.endswith('failed'):
                    summary['failed'] = int(part.replace('failed', ''))
                elif part.endswith('skipped'):
                    summary['skipped'] = int(part.replace('skipped', ''))
            summary['total'] = summary['passed'] + summary['failed'] + summary['skipped']
            break
    
    return summary

def print_summary(summary):
    """Print formatted test summary"""
    print("\n" + "=" * 60)
    print("📊 TEST SUITE SUMMARY")
    print("=" * 60)
    print(f"Total tests: {summary.get('total', 0)}")
    print(f"Passed:      {summary.get('passed', 0)}")
    print(f"Failed:      {summary.get('failed', 0)}")
    print(f"Skipped:     {summary.get('skipped', 0)}")
    print(f"Duration:    {summary.get('duration', 0):.2f} seconds")
    
    # Check if all tests passed
    if summary.get('failed', 0) == 0 and summary.get('total', 0) > 0:
        print("\n✅ ALL TESTS PASSED!")
    elif summary.get('total', 0) == 0:
        print("\n⚠️  NO TESTS FOUND")
    else:
        print("\n❌ SOME TESTS FAILED")

if __name__ == "__main__":
    success = run_canonical_suite()
    sys.exit(0 if success else 1)
