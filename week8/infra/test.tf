# locals {
#   vars = {
#     tier        = "backend",
#     FLASK_APP   = "run.py",
#     FLASK_DEBUG = 1,
#   }
# }


# #  environment = [
# #         { "name" : "Owner", "value" : "Akhilesh" },
# #         { "name" : "DB_LINK", "value" : "postgresql://${aws_db_instance.postgres.username}:${random_password.password.result}@${aws_db_instance.postgres.address}:5432/${aws_db_instance.postgres.db_name}" }
# #       ]

# output "env_dat" {
#   value = [

#     for key, value in local.vars : {
#       name  = key
#       value = value
#     }
#   ]
# }