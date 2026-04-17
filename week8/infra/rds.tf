
# some aditional changes 

resource "aws_subnet" "rds" {
  count             = length(var.rds_subnet)
  vpc_id            = module.network.vpc_id
  cidr_block        = var.rds_subnet[count.index].cidr
  availability_zone = var.rds_subnet[count.index].availability_zone

  tags = {
    Name = "${var.vpc_name}-${var.rds_subnet[count.index].name}"
  }
}
#  subnet group

resource "aws_db_subnet_group" "default" {
  name       = "${var.prefix}-${var.app_name}-db-subnet-group"
  subnet_ids = aws_subnet.rds[*].id

}

# password (A-Za-z0-9) - > secrets manager -> random_password.password.result
resource "random_password" "password" {
  length           = 10
  special          = false
  override_special = "abchjkmnpqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
}

# output "password" {
#   value     = random_password.password.result
#   sensitive = true
# }

# secret manage create
resource "aws_secretsmanager_secret" "db_link" {
  name = "${var.prefix}-${var.app_name}-db_link"
}

# create secret in secrets manager(version)
# "postgresql://postgres:Admin1234@jan26week5studentportal.cvik8accw2tk.ap-south-1.rds.amazonaws.com:5432/studentportal"}
resource "aws_secretsmanager_secret_version" "db_link_version" {
  secret_id     = aws_secretsmanager_secret.db_link.id
  secret_string = "postgresql://${aws_db_instance.postgres.username}:${random_password.password.result}@${aws_db_instance.postgres.address}:5432/${aws_db_instance.postgres.db_name}"

}

resource "aws_secretsmanager_secret" "dbusername" {
  name = "${var.prefix}-${var.app_name}-db_username"
}

# create secret in secrets manager(version)
# "postgresql://postgres:Admin1234@jan26week5studentportal.cvik8accw2tk.ap-south-1.rds.amazonaws.com:5432/studentportal"}
resource "aws_secretsmanager_secret_version" "db_username_version" {
  secret_id     = aws_secretsmanager_secret.dbusername.id
  secret_string = aws_db_instance.postgres.username
}

resource "aws_secretsmanager_secret" "db_password" {
  name = "${var.prefix}-${var.app_name}-db_password"
}

# create secret in secrets manager(version)
# "postgresql://postgres:Admin1234@jan26week5studentportal.cvik8accw2tk.ap-south-1.rds.amazonaws.com:5432/studentportal"}
resource "aws_secretsmanager_secret_version" "db_password_version" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.password.result
}



# rds instance -> aws_db_instance.postgres.username
resource "aws_db_instance" "postgres" {
  identifier             = "${var.prefix}-${var.app_name}-db"
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "15.14"
  instance_class         = "db.t3.micro"
  db_name                = "studentportal"
  username               = "postgres"
  password               = random_password.password.result
  db_subnet_group_name   = aws_db_subnet_group.default.name
  skip_final_snapshot    = true
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.rds.id]
  # vpc_security_group_ids = ["sg-0f4dc87e4139cf956"]
}


# output "dbhost" {
#   value = aws_db_instance.postgres.address
# }