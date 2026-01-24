from src.sis.engine import RuleEngine
import json

# Load the rules
engine = RuleEngine("rules/canonical.json")

# Test resource that should trigger IRR-DEC-02
test_resource = {
    "kind": "aws_s3_bucket",
    "name": "logs",
    "data": {
        "lifecycle": {
            "prevent_destroy": True
        }
    },
    "line": 4
}

# Scan it
findings = engine.scan_resource("terraform", "aws_s3_bucket", test_resource)
print("Findings:", findings)
print("\nAll rules loaded:", len(engine.rules))

# Check IRR-DEC-02 specifically
irr_dec_02 = engine.rules_by_id.get("IRR-DEC-02")
if irr_dec_02:
    print("\nIRR-DEC-02 details:")
    print(f"  File types: {irr_dec_02.file_types}")
    print(f"  Resource kinds: {irr_dec_02.resource_kinds}")
    print(f"  Conditions: {[(c.path, c.operator, c.value) for c in irr_dec_02.conditions]}")
    print(f"  Matches file type 'terraform'? {irr_dec_02.matches_file_type('terraform')}")
    print(f"  Matches resource kind 'aws_s3_bucket'? {irr_dec_02.matches_resource_kind('aws_s3_bucket')}")
    print(f"  Rule evaluates to: {irr_dec_02.evaluate(test_resource)}")
