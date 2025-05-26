output "abstract_lambda_function_arn" {
  value = aws_lambda_function.abstract_lambda_function.arn
}

output "abstract_lambda_function_name" {
  value = aws_lambda_function.abstract_lambda_function.function_name
}

output "abstract_lambda_role_name" {
  value = aws_iam_role.iam_for_lambda.name
}
