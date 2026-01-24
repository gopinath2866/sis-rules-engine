# Simple Terraform that matches parser expectations
resource "aws_s3_bucket" "test_bucket" {
  bucket = "test"
  acl    = "public-read"
}

resource "aws_iam_policy" "test_policy" {
  name = "test"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "*"
      Resource = "*"
    }]
  })
}
