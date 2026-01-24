#!/usr/bin/env python3
"""
Run the canonical test suite and produce a summary
"""
import subprocess
import json
import sys
from pathlib import Path

def run_canonical_suite():
    """Execute the canonical test suite"""
    print("🚀 Running SIS v1.0.0 Canonical Test Suite...")
    print("=" * 60)
    
    # Run pytest with JUnit output
    result = subprocess.run([
        "pytest", "tests/",
        "-v",
        "--tb=short",
        "--junitxml=test-results/canonical.xml",
        "--json-report",
        "--json-report-file=test-results/report.json"
    ], capture_output=True, text=True)
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    # Load and display JSON report
    report_path = Path("test-results/report.json")
    if report_path.exists():
        with open(report_path) as f:
            report = json.load(f)
        
        summary = report.get("summary", {})
        print("\n" + "=" * 60)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 60)
        print(f"Total tests: {summary.get('total', 0)}")
        print(f"Passed:      {summary.get('passed', 0)}")
        print(f"Failed:      {summary.get('failed', 0)}")
        print(f"Skipped:     {summary.get('skipped', 0)}")
        print(f"Duration:    {summary.get('duration', 0):.2f} seconds")
        
        # Check if all tests passed
        if summary.get('failed', 0) == 0:
            print("\n✅ ALL TESTS PASSED!")
            return True
        else:
            print("\n❌ SOME TESTS FAILED")
            return False
    else:
        print("\n⚠️  No report generated")
        return False

if __name__ == "__main__":
    # Create test-results directory
    Path("test-results").mkdir(exist_ok=True)
    
    success = run_canonical_suite()
    sys.exit(0 if success else 1)