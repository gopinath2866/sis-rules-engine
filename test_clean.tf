# Clean Terraform file for testing
resource "aws_s3_bucket" "public_data" {
  bucket = "company-public-data"
  acl    = "public-read-write"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_iam_policy" "admin_policy" {
  name = "admin-policy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
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
    cidr_blocks = ["0.0.0.0/0"]
  }
}

variable "database_password" {
  description = "Database password"
  default     = "supersecret123"
}
