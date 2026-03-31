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

variable "app_name" {
  default = "student-portal"
}

variable "prefix" {
  default = "jan26-bootcamp"
}

variable "image" {
  type    = string
  default = "879381241087.dkr.ecr.ap-south-1.amazonaws.com/jan26week5-studentportal:1.0"
}

variable "container_port" {
  type    = number
  default = 8000
}

variable "db_link" {
  type    = string
  default = "postgresql://postgres:Admin1234@jan26week5studentportal.cvik8accw2tk.ap-south-1.rds.amazonaws.com:5432/studentportal"
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