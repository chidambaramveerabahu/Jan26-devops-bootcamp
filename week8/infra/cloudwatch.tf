resource "aws_cloudwatch_log_group" "ecs_logs" {
  for_each          = local.ecs_services_map
  name              = "/ecs/${var.app_name}-${each.key}"
  retention_in_days = 7
}
