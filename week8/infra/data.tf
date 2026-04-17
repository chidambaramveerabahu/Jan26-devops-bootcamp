data "aws_route53_zone" "app" {
  name         = var.domain_name
  private_zone = false
}
