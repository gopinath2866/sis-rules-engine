import sys
sys.path.insert(0, 'src')

from sis.parsers.terraform import parse_file
from sis.engine import RuleEngine

content = '''resource "aws_s3_bucket" "logs" {
  bucket = "my-logs"
  lifecycle {
    prevent_destroy = true
  }
}'''

print("=== TESTING PARSER ===")
result = parse_file(content)
print("Parsed resource:", result[0])

print("\n=== TESTING RULE MATCH ===")
engine = RuleEngine("rules/canonical.json")
irr_dec_02 = engine.rules_by_id["IRR-DEC-02"]

resource = result[0]
print(f"Resource kind: {resource['kind']}")
print(f"Has 'lifecycle' key: {'lifecycle' in resource}")
print(f"Has 'lifecycle.prevent_destroy': {'lifecycle' in resource and 'prevent_destroy' in resource['lifecycle']}")
print(f"Rule evaluates: {irr_dec_02.evaluate(resource)}")

# Manual check
if 'lifecycle' in resource and 'prevent_destroy' in resource['lifecycle']:
    print(f"Value of lifecycle.prevent_destroy: {resource['lifecycle']['prevent_destroy']}")
