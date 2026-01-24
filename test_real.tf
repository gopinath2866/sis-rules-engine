# Real Terraform file with multiple issues
resource "aws_s3_bucket" "public_data" {
  bucket = "company-public-data"
  acl    = "public-read-write"  # This should trigger TF-001

  lifecycle {
    prevent_destroy = true  # This should trigger IRR-DEC-02
  }
}

resource "aws_iam_policy" "admin_policy" {
  name = "admin-policy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"  # This should trigger IRR-DEC-01
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
    cidr_blocks = ["0.0.0.0/0"]  # This should trigger TF-002
  }
}

# Plaintext secret (should trigger TF-003)
variable "database_password" {
  description = "Database password"
  default     = "supersecret123"
}

# Another secret in resource
resource "aws_instance" "web_server" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  
  user_data = <<-EOF
    #!/bin/bash
    DB_PASSWORD="anothersecret456"
    echo "Starting server..."
  EOF
}
