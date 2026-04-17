resource "aws_ecs_cluster" "main" {
  name = "${var.prefix}-${var.app_name}-cluster"

  service_connect_defaults {
    namespace = aws_service_discovery_http_namespace.main.arn
  }
}

# Define the Namespace
resource "aws_service_discovery_http_namespace" "main" {
  name        = "${var.prefix}-${var.app_name}-namespace"
  description = "Dev name space"
}


resource "aws_ecs_task_definition" "service" {
  for_each                 = local.ecs_services_map
  family                   = "${var.prefix}-${var.app_name}-${each.key}-task"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = each.value.cpu
  memory                   = each.value.memory
  container_definitions = jsonencode([
    {
      name      = "${var.app_name}-${each.key}"
      image     = "${local.ecr_registry}/${each.value.ecr_repository}:latest"
      cpu       = each.value.cpu
      memory    = each.value.memory
      essential = true
      portMappings = [
        {
          name          = each.value.name
          containerPort = tonumber(each.value.port)
          hostPort      = tonumber(each.value.port)
        }
      ]
      environment = [
        for key, value in each.value.vars : {
          name  = key
          value = tostring(value)
        }
      ]
      secrets = [
        for key, value in lookup(each.value, "secrets", {}) : {
          name      = key
          valueFrom = value
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_logs[each.key].name
          awslogs-region        = "ap-south-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}


# ecs services  



resource "aws_ecs_service" "service" {
  for_each        = local.ecs_services_map
  name            = "${var.prefix}-${var.app_name}-${each.key}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.service[each.key].arn
  desired_count   = each.value.desired_count
  launch_type     = "FARGATE"


  network_configuration {
    subnets          = module.network.private_subnet_ids
    security_groups  = [aws_security_group.ecs[each.key].id]
    assign_public_ip = false
  }
  dynamic "load_balancer" {
    for_each = each.value.if_load_balancer ? [1] : []
    content {
      target_group_arn = aws_lb_target_group.app_tg.arn
      container_name   = "${var.app_name}-${each.key}"
      container_port   = tonumber(each.value.port)
    }
  }

  service_connect_configuration {
    enabled   = true
    namespace = aws_service_discovery_http_namespace.main.arn

    service {
      port_name      = each.value.name
      discovery_name = each.value.name

      client_alias {
        dns_name = each.value.name
        port     = tonumber(each.value.port)
      }
    }


  }
}

