# This should trigger multiple rules
resource "aws_s3_bucket" "public_data" {
  bucket = "company-public-data"
  acl    = "public-read-write"  # TF-002: Public S3 bucket
}

resource "aws_iam_policy" "admin" {
  name = "admin-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "*"  # TF-001: Admin IAM policy
        Resource = "*"
      }
    ]
  })
}

resource "aws_security_group" "open_ssh" {
  name = "open-ssh"
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # TF-002: Open security group
  }
}

# Plaintext secret (should trigger TF-003)
variable "db_password" {
  default = "supersecret123"
}
