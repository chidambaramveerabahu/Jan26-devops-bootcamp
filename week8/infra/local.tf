locals {

  # 2 ecs services

  ecr_registry = "879381241087.dkr.ecr.ap-south-1.amazonaws.com"

  ecs_services = [
    {
      name             = "frontend"
      container        = "frontend"
      port             = "80"
      cpu              = 512
      memory           = 1024
      desired_count    = 1
      ecr_repository   = "${var.app_name}-frontend"
      if_load_balancer = true
      trafic_from      = "alb"
      vars = {
        tier        = "frontend",
        BACKEND_URL = "http://backend:${var.backend_port}",

      }
    },
    {
      name             = "backend"
      container        = "backend"
      port             = "8000"
      cpu              = 512
      memory           = 1024
      desired_count    = 1
      if_load_balancer = false
      ecr_repository   = "${var.app_name}-backend"
      tag              = "latest"
      # image = "${local.ecr_registry}/${local.ecr_repository}:${local.tag}"
      vars = {
        tier        = "backend",
        FLASK_APP   = "run.py",
        FLASK_DEBUG = 1,
        DB_PORT     = "5432",
        DB_HOST     = "${aws_db_instance.postgres.address}",
        DB_NAME     = "${aws_db_instance.postgres.db_name}",
        SECRET_KEY  = "your-secret-key-here",
        # use secrets 
        #   DATABASE_URL="${aws_secretsmanager_secret_version.db_password_version.secret_string}",
        #   # give a encrypted string in secrets manager and then use it here as env variable
        # #   SECRET_KEY=your-secret-key-here,
        #   DB_HOST="${aws_db_instance.postgres.address}",
        #   DB_PORT=5432,
        #   DB_NAME="${aws_db_instance.postgres.db_name}",
        #   DB_USERNAME="${aws_db_instance.postgres.username}",
        #   # use as secrets
        #   DB_PASSWORD="${random_password.password.result}",
        ALLOWED_ORIGINS = "http://frontend:80,https://${aws_lb.app_alb.dns_name}"
      },
      secrets = {
        # use secrets 

        DATABASE_URL = aws_secretsmanager_secret.db_link.arn,
        # give a encrypted string in secrets manager and then use it here as env variable
        DB_USERNAME = aws_secretsmanager_secret.dbusername.arn,
        # use as secrets
        DB_PASSWORD = aws_secretsmanager_secret.db_password.arn,
      },
    }

  ]



  #   test_ecs = {
  #     # key1 = "value1",
  #     # key2 = "value2"

  #     frontend = {
  #       name           = "frontend"
  #       container      = "frontend"
  #       port           = "80"
  #       ecr_repository = "${var.app_name}-frontend"
  #     },
  #     backend = {
  #       name           = "backend"
  #       container      = "backend"
  #       port           = "8000"
  #       ecr_repository = "${var.app_name}-backend"
  #     }
  #   }

  ecs_services_map = {
    for service in local.ecs_services : service.name => service
  }


  something_randoon = "this is a random local variable"
}

# 