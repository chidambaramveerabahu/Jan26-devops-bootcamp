# ECS repo to store app image 

resource "aws_ecr_repository" "app_image" {
  name = "${var.prefix}-${var.app_name}"
}

# output "repo_link" {
#   value = aws_ecr_repository.app_image.repository_url
# }
## ECS componenets
# ECS cluster


resource "aws_ecs_cluster" "app_cluster" {
  name = "${var.prefix}-${var.app_name}"

  #   setting {
  #     name  = "containerInsights"
  #     value = "enabled"
  #   }
}

# Task definition
resource "aws_ecs_task_definition" "service" {
  family                   = "${var.prefix}-${var.app_name}-task"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  container_definitions = jsonencode([
    {
      name      = var.app_name
      image     = var.image
      cpu       = 1024
      memory    = 2048
      essential = true
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
        }
      ]
      environment = [
        { "name" : "Owner", "value" : "Akhilesh" },
        { "name" : "DB_LINK", "value" : "postgresql://${aws_db_instance.postgres.username}:${random_password.password.result}@${aws_db_instance.postgres.address}:5432/${aws_db_instance.postgres.db_name}" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-create-group  = "true"
          awslogs-group         = "/ecs/jan26week5-studentportal"
          awslogs-region        = "ap-south-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}


# ECS service

resource "aws_ecs_service" "service" {
  name            = "${var.prefix}-${var.app_name}-service"
  cluster         = aws_ecs_cluster.app_cluster.id
  task_definition = aws_ecs_task_definition.service.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.private1.id, aws_subnet.private2.id]
    security_groups = [aws_security_group.ecs.id]
    assign_public_ip = false
  }
}