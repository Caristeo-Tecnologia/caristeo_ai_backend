data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam-for-${var.lambda_function_name}"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = var.lambda_source_dir
  output_path = "${var.lambda_output_path}/${var.lambda_function_name}.zip"
}

resource "aws_lambda_function" "abstract_lambda_function" {
  filename      = data.archive_file.lambda.output_path
  function_name = var.lambda_function_name
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = var.lambda_function_handler
  timeout       = var.timeout
  layers        = var.lambda_layers

  source_code_hash = data.archive_file.lambda.output_base64sha256
  memory_size      = var.memory_size

  runtime = var.runtime

  environment {
    variables = var.environment_variables
  }
}
