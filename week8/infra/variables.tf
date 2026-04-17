variable "aws_region" {
  type        = string
  description = "aws region"
  default     = "ap-south-1"
}

variable "vpc_name" {
  type        = string
  description = "vpc name"
  default     = "jan26week6"
}

# var.vpc_name
# "var.vpc_name-public1-subnet"
# string interpolation -> "${var.vpc_name}-public1"


variable "primary_az" {
  type        = string
  description = "primary availability zone"
  default     = "ap-south-1a"
}

variable "secondary_az" {
  type        = string
  description = "secondary availability zone"
  default     = "ap-south-1b"
}

variable "prefix" {
  default = "jan26-bootcamp"
}


variable "container_port" {
  type    = number
  default = 8000
}


variable "domain_name" {
  type    = string
  default = "livingdevops.org"
}

variable "alb_zone_id" {
  type        = string
  description = "zone id for ALB on a certain region"
  default     = "Z11ORPS3UI2S3F"
}

variable "alb_port_list" {
  type = list(map(string))
  default = [
    { "from_port" = "80", "to_port" = "80" },
    { "from_port" = "443", "to_port" = "443" }
  ]
}


variable "rds_subnet" {
  type        = list(map(string))
  description = "cidr and azs"
  default = [
    { "name" = "", "cidr" = "", "availability_zone" = "" },
    { "name" = "", "cidr" = "", "availability_zone" = "" }
  ]
}


###### ecs seervices part ###

variable "app_name" {
  type    = string
  default = "devopsdozo"
}

# backend
variable "backend_port" {
  type    = number
  default = 8000
}


# frontend

variable "frontend_port" {
  type    = number
  default = 80
}