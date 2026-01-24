from src.sis.parsers.terraform import parse_file

content = '''resource "aws_s3_bucket" "logs" {
  bucket = "my-logs"
  lifecycle {
    prevent_destroy = true
  }
}'''

result = parse_file(content)
print("Parser output:")
print(result)
print("\nFirst resource data:")
if result:
    print(result[0].get('data', {}))
