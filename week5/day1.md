repo: 879381241087.dkr.ecr.ap-south-1.amazonaws.com/jan26-week5

repo: <aws_account_id>.dkr.ecr.<aws-region>.amazonaws.com/<ecr_repo_name>


aws configure 

aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 879381241087.dkr.ecr.ap-south-1.amazonaws.com



aws ecr get-login-password --region ap-south-1

879381241087.dkr.ecr.ap-south-1.amazonaws.com/jan26-week5:1.0