import sys
sys.path.insert(0, 'src')

from sis.parsers.terraform import parse_file
from sis.engine import RuleEngine

# Test content
content = '''resource "aws_s3_bucket" "logs" {
  bucket = "my-logs"
  lifecycle {
    prevent_destroy = true
  }
}'''

print("=== PARSER TEST ===")
result = parse_file(content)
print("Parser output:", result)
if result:
    print("First resource data:", result[0].get('data', {}))

print("\n=== RULE ENGINE TEST ===")
engine = RuleEngine("rules/canonical.json")
print(f"Loaded {len(engine.rules)} rules")

# Check IRR-DEC-02
irr_dec_02 = engine.rules_by_id.get("IRR-DEC-02")
print(f"\nIRR-DEC-02 exists: {irr_dec_02 is not None}")

if result and irr_dec_02:
    resource = result[0]
    print(f"\nTesting resource: {resource['kind']} '{resource['name']}'")
    print(f"Rule matches file type 'terraform': {irr_dec_02.matches_file_type('terraform')}")
    print(f"Rule matches resource kind '{resource['kind']}': {irr_dec_02.matches_resource_kind(resource['kind'])}")
    print(f"Rule evaluates: {irr_dec_02.evaluate(resource)}")
    
    # Test the condition directly
    if irr_dec_02.conditions:
        cond = irr_dec_02.conditions[0]
        print(f"\nCondition: path='{cond.path}', operator='{cond.operator}', value='{cond.value}'")
        print(f"Condition evaluates: {cond.evaluate(resource)}")
        
        # Debug path traversal
        print(f"\nPath '{cond.path}' traversal:")
        parts = cond.path.split('.')
        current = resource
        for part in parts:
            print(f"  Looking for '{part}' in {type(current)}: {part in current if isinstance(current, dict) else 'N/A'}")
            if isinstance(current, dict) and part in current:
                current = current[part]
                print(f"    Found: {current}")
            else:
                print(f"    NOT FOUND")
                break
