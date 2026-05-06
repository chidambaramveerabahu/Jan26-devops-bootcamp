module "lambda_function" {
    for_each = local.lambda_functions
  source = "terraform-aws-modules/lambda/aws"
  version = "8.7.0"

  function_name = each.value.function_name
  description   = each.value.description
  handler       = each.value.handler
  runtime       = "python3.14"
  publish       = true
  create_role   = false
  lambda_role  = aws_iam_role.lambda_role.arn
  source_path = each.value.source_dir

  store_on_s3 = true
  s3_bucket   = "clean-bucket-879381241087"

#   layers = [
#     module.lambda_layer_s3.lambda_layer_arn,
#   ]

  environment_variables = {
    Serverless = "Terraform"
  }

  tags = {
    Module = "lambda-with-layer"
  }
}

# module "lambda_layer_s3" {
#   source = "terraform-aws-modules/lambda/aws"

#   create_layer = true

#   layer_name          = "lambda-layer-s3"
#   description         = "My amazing lambda layer (deployed from S3)"
#   compatible_runtimes = ["python3.12"]

#   source_path = "../src/lambda-layer"

#   store_on_s3 = true
#   s3_bucket   = "my-bucket-id-with-lambda-builds"
# }