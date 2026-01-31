# CANONICAL TEST: IRR-DEC-01
# This file is part of the SIS Golden Rule test suite

# 1. Should trigger: aws_rds_cluster with deletion_protection = true
resource "aws_rds_cluster" "production" {
  cluster_identifier = "prod-cluster"
  engine            = "aurora"
  deletion_protection = true
}

# 2. Should NOT trigger: aws_rds_cluster with deletion_protection = false
resource "aws_rds_cluster" "staging" {
  cluster_identifier = "staging-cluster"
  engine            = "aurora"
  deletion_protection = false
}

# 3. Should NOT trigger: aws_rds_cluster without deletion_protection
resource "aws_rds_cluster" "development" {
  cluster_identifier = "dev-cluster"
  engine            = "aurora"
}

# 4. Should NOT trigger: non-RDS resource with deletion_protection
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  deletion_protection = true  # Different resource type, different rule
}
