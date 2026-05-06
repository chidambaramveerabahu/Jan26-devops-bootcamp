# # zip my lambda function
# data "archive_file" "function1" {
#     type = "zip"
#     # source directory is the directory that contains the lambda function -> ../functions/function1
#     source_dir = "${path.module}/../functions/function1"
#     output_path = "${path.module}/../functions/function1/function1.zip"
# }   

# # create lambda function
# resource "aws_lambda_function" "function1" {
#     function_name = "lambda-terraform-projects-function1"
#     filename = data.archive_file.function1.output_path
#     # handler file.function name
#     handler = "create_ec2.lambda_handler"
#     # runtime is the runtime environment for the lambda function
#     runtime = "python3.14"
#     # role is the IAM role that will be used to execute the lambda function
#     role = aws_iam_role.lambda_role.arn
#     # environment variables are the environment variables that will be used to execute the lambda function
#     timeout = 10
#     memory_size = 128
#     source_code_hash = data.archive_file.function1.output_base64sha256
#     environment {
#         variables = {
#             "ENV" = "dev"
#         }
#     }

#     tags = {
#         repo = "jan26-bootcamp/lambda-terraform-projects"
#         terraform = "true"
#     }
# }


# # zip my lambda function
# data "archive_file" "function2" {
#     type = "zip"
#     # source directory is the directory that contains the lambda function -> ../functions/function1
#     source_dir = "${path.module}/../functions/function2"
#     output_path = "${path.module}/../functions/function2/function2.zip"
# }   

# # create lambda function
# resource "aws_lambda_function" "function2" {
#     function_name = "lambda-terraform-projects-function2"
#     filename = data.archive_file.function2.output_path
#     # handler file.function name
#     handler = "terminate_ec2.lambda_handler"
#     # runtime is the runtime environment for the lambda function
#     runtime = "python3.14"
#     # role is the IAM role that will be used to execute the lambda function
#     timeout = 10
#     memory_size = 128
#     role = aws_iam_role.lambda_role.arn
#     # environment variables are the environment variables that will be used to execute the lambda function
#     source_code_hash = data.archive_file.function2.output_base64sha256
#     environment {
#         variables = {
#             "ENV" = "dev"
#         }
#     }

#     tags = {
#         repo = "jan26-bootcamp/lambda-terraform-projects"
#         terraform = "true"
#     }
# }
