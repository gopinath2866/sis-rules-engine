# Example infrastructure with security issues
resource "aws_s3_bucket" "data" {
  bucket = "my-company-data"
  acl    = "public-read"  # Public bucket
  
  # No encryption configured
}

resource "aws_security_group" "web" {
  name = "web-sg"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Open to internet
  }
}

resource "aws_iam_policy" "admin" {
  name = "AdminPolicy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "*"  # Admin access
      Resource = "*"
    }]
  })
}

# Plaintext secret
variable "api_key" {
  description = "API key for service"
  default     = "sk_live_abc123secret"
}
