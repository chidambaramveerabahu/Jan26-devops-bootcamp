resource "aws_ecr_repository" "my_repo" {
  for_each = local.ecs_services_map
  name     = each.value.ecr_repository
}



# go to the directory where your Dockerfile is located and run the following command to build the Docker image and push it to ECR:

# App code is at : Jan26-devops-bootcamp/DevOpsDojo

# 879381241087.dkr.ecr.ap-south-1.amazonaws.com/devopsdozo-backend
# 879381241087.dkr.ecr.ap-south-1.amazonaws.com/devopsdozo-frontend

# on backend directory
# docker build  -t 879381241087.dkr.ecr.ap-south-1.amazonaws.com/devopsdozo-backend:latest  --platform linux/amd64  .
# on frontend directory
# docker build -t 879381241087.dkr.ecr.ap-south-1.amazonaws.com/devopsdozo-frontend:latest  --platform linux/amd64 .


# ecr login
# aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 879381241087.dkr.ecr.ap-south-1.amazonaws.com 

# docker push 879381241087.dkr.ecr.ap-south-1.amazonaws.com/devopsdozo-backend:latest
# docker push 879381241087.dkr.ecr.ap-south-1.amazonaws.com/devopsdozo-frontend:latest