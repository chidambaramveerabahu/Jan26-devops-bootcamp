# public hosted zone -> data source

data "aws_route53_zone" "app" {
  name         = var.domain_name
  private_zone = false
}

# output "public_hoisted_zone" {
#   value = data.aws_route53_zone.app.name
# }
