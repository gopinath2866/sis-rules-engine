#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

from sis.scanner import SISScanner
from sis.cli import generate_output

scanner = SISScanner()
findings = scanner.scan_file("test_clean.tf")

print("🧪 Debugging JSON Output")
print("=" * 60)
print(f"Number of findings: {len(findings)}")
print(f"First finding: {findings[0] if findings else 'None'}")

# Try to generate JSON
try:
    json_output = generate_output(findings, 'json', "test_clean.tf")
    print(f"\n✅ JSON generated successfully!")
    print(f"Length: {len(json_output)} chars")
    print(f"First 200 chars:\n{json_output[:200]}")
    
    # Try to parse it
    import json
    parsed = json.loads(json_output)
    print(f"\n✅ JSON parsed successfully!")
    print(f"Structure: {type(parsed)}")
    print(f"Keys: {list(parsed.keys())}")
    
except Exception as e:
    print(f"\n❌ Error generating JSON: {e}")
    import traceback
    traceback.print_exc()
