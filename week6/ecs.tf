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

    load_balancer {
        target_group_arn = aws_lb_target_group.app_tg.arn
        container_name   = var.app_name
        container_port   = var.container_port
    }

}




# app autoscaling
resource "aws_appautoscaling_target" "ecs_scaling_target" {
  max_capacity       = 3
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.app_cluster.name}/${aws_ecs_service.service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
} 

resource "aws_appautoscaling_policy" "cpu_scaling_policy" {
  name               = "${var.prefix}-${var.app_name}-cpu-scaling-policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_scaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_scaling_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_scaling_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 70.0
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    scale_in_cooldown  = 100
    scale_out_cooldown = 300
  }
}
