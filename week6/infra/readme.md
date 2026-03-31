# ECS - 3 tier app - Terraform

- VPC
 - 2 private subnet
 - 2 public subnet
 - 2 rds subnet (private)

 - 2 Route tables
 - associate private/public subnet to respective RT
 - 1 Nat gateway - private AZ (zone)
 - routes for public and private

 - 3 SG for rds, ecs and ALB
 - open the port wherever needed


 - ALB
   - Target group
   - ALb (public subnet (min 2))
   - Listener for Http port 80
   - ACM cert for ssl
   - Listen for https - 443
   - WAF 

- APP
 - ecr repo
 - push app image ( manual way)

 - ECS task defnition 
 - ECS cluster
 - ECS services
 - APP autoscaling (manual and TF)

- DNS
 - route 53 public zone
 - create a route to ALB
 - ACM cert validation

- DB
 - rds 
 - secret manager for password
 - generate a random password
 - Create KMS key for db 



# Terraform drift ->  manaual change in cloud resources
- in plan it will tell to create and in apply it will create 



# how to import 

import {
  to = aws_ecs_task_definition.manualimport
  id = "arn:aws:ecs:ap-south-1:879381241087:task-definition/jan26week5-studentportal:4"
}

# run command 
terraform plan -generate-config-out=manualimportedstuff.tf





aws secretsmanager delete-secret \
    --secret-id jan26-bootcamp-student-portal-db\
    --force-delete-without-recovery


aws ecs describe-task-definition --task-definition jan26-bootcamp-student-portal-task --query taskDefinition 


          jq --arg IMAGE 879381241087.dkr.ecr.ap-south-1.amazonaws.com/jan26-bootcamp-student-portal '.containerDefinitions[0].image = $IMAGE' task-definition.json > updated-task-definition.json
