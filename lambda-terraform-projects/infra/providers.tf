terraform {
  backend "s3" {
    bucket = "state-bucket-879381241087"
    key    = "jan26-devops-bootcamp/lambda-terraform-projects/terraform.tfstate"
    region = "ap-south-1"
  }
}
