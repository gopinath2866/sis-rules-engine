# Database configuration
resource "aws_db_instance" "mysql" {
  identifier     = "prod-mysql"
  engine         = "mysql"
  instance_class = "db.t3.micro"
  
  username = "admin"
  password = "SuperSecretPassword123!"  # Plaintext password
  
  allocated_storage = 20
}
