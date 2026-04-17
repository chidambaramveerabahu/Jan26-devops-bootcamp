# ALB 
resource "aws_lb" "app_alb" {
  name               = "${var.prefix}-${var.app_name}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  # public subnets for alb
  subnets = module.network.public_subnet_ids
}



# Target group
resource "aws_lb_target_group" "app_tg" {
  name        = "${var.prefix}-${var.app_name}"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = module.network.vpc_id
  target_type = "ip"

  health_check {
    enabled = true
    port    = 80
    path    = "/health"

  }
}

# Listener
resource "aws_lb_listener" "app_listener" {
  load_balancer_arn = aws_lb.app_alb.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}

# https listener
resource "aws_lb_listener" "app_https_listener" {
  load_balancer_arn = aws_lb.app_alb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate.app_cert.arn
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}