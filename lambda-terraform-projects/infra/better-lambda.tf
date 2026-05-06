

# # zip my lambda function


# data "archive_file" "function" {
#     for_each = local.lambda_functions
#     type = "zip"
#     # source directory is the directory that contains the lambda function -> ../functions/function1
#     source_dir = "${path.module}/${each.value.source_dir}"
#     output_path = "${path.module}/${each.value.source_dir}/${each.value.function_name}.zip"

# }

# # create lambda function
# resource "aws_lambda_function" "function" {
#     for_each = local.lambda_functions
#     function_name = each.value.function_name
#     filename = data.archive_file.function[each.key].output_path
#     handler = each.value.handler
#     runtime = "python3.14"
#     role = aws_iam_role.lambda_role.arn
#     timeout = 10
#     memory_size = 128
#     source_code_hash = data.archive_file.function[each.key].output_base64sha256
#     tags = {
#         repo = "jan26-bootcamp/lambda-terraform-projects"
#         terraform = "true"
#     }
# }

