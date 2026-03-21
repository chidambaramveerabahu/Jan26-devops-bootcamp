provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      repo      = "jan26-bootcamp"
      terraform = "true"
    }
  }
}

# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY


terraform {
  backend "s3" {
    bucket  = "state-bucket-879381241087"
    key     = "jan26/week6/terraform.tfstate"
    region  = "ap-south-1"
    encrypt = true
  }
}