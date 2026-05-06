locals {
  lambda_functions = {
    function1 = {
      function_name = "lambda-create-ec2"
      source_dir = "../functions/function1"
      handler = "create_ec2.lambda_handler"
      description = "Create EC2 instance"
    }
 
  function2 = {
    function_name = "lambda-terminate-ec2"
    source_dir = "../functions/function2"
    handler = "terminate_ec2.lambda_handler"
    description = "Terminate EC2 instance"
    }
  function3 = {
    function_name = "lambda-hello-world"
    source_dir = "../functions/function3"
    handler = "main.lambda_handler"
    description = "Hello World"
    }
  }
}

# for_each =  local.lambda_functions