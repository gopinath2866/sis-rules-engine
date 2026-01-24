# Production Infrastructure for E-commerce Platform
resource "aws_s3_bucket" "customer_data" {
  bucket = "prod-customer-data-2024"
  acl    = "private"  # Good - private
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  
  lifecycle {
    prevent_destroy = true  # Critical data - cannot be deleted
  }
}

resource "aws_s3_bucket" "public_assets" {
  bucket = "prod-assets-public"
  acl    = "public-read"  # Public assets for website
  
  # No encryption - BAD!
}

resource "aws_security_group" "database_sg" {
  name        = "database-security-group"
  description = "Database access"
  
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]  # Good - restricted to VPC
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]  # Bad - allows all outbound
  }
}

resource "aws_security_group" "web_sg" {
  name        = "web-security-group"
  description = "Web server access"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Bad - open to world
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Bad - open to world
  }
}

resource "aws_iam_policy" "ec2_full_access" {
  name = "EC2FullAccess"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ec2:*"  # Too broad but not admin
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy" "admin_policy" {
  name = "AdministratorAccess"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"  # ⚠️ CRITICAL - Admin access!
        Resource = "*"
      }
    ]
  })
}

# Secrets in plaintext - BAD!
variable "stripe_api_key" {
  description = "Stripe API key for payments"
  default     = "sk_live_51Hx...secret..."  # ⚠️ Plaintext secret!
}

resource "aws_db_instance" "postgres" {
  identifier     = "prod-postgres"
  engine         = "postgres"
  instance_class = "db.r5.large"
  
  username = "admin"
  password = "SuperSecretDBPassword123!"  # ⚠️ Plaintext password!
  
  storage_encrypted = true  # Good - encryption enabled
}
