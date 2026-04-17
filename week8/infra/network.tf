# creating network from https://github.com/akhileshmishrabiz/network-module module 

module "network" {
  source = "git::https://github.com/akhileshmishrabiz/network-module.git?ref=v1.1.2"

  vpc_cidr = "10.0.0.0/16"
  vpc_name = "ecs-vpc"

  need_nat_gateway        = true
  need_single_nat_gateway = true
  enable_dns_hostnames    = true
  enable_dns_support      = true

  private_subnet_data = [
    {
      cidr              = "10.0.1.0/24"
      availability_zone = "ap-south-1a"
      prefix            = "private"
    },
    {
      cidr              = "10.0.2.0/24"
      availability_zone = "ap-south-1b"
      prefix            = "private"
    }
  ]

  public_subnet_data = [
    {
      cidr              = "10.0.3.0/24"
      availability_zone = "ap-south-1a"
      prefix            = "public"
    },
    {
      cidr              = "10.0.4.0/24"
      availability_zone = "ap-south-1b"
      prefix            = "public"
    }
  ]
}

# output "vpc_id" {
#   value = module.network.vpc_id
# }

# output "public_subnet_ids" {
#   value = module.network.public_subnet_ids
# }

# output "private_subnet_ids" {
#   value = module.network.private_subnet_ids
# }