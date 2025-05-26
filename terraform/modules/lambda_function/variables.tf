variable "lambda_function_name" {
  description = "The name of the Lambda function."
  type        = string
  default     = "split_n_convert_pdf_lambda"
}

variable "lambda_source_dir" {
  description = "The source directory for the Lambda function."
  type        = string
}

variable "lambda_output_path" {
  description = "The output path for the Lambda function zip file."
  type        = string
}

variable "lambda_function_handler" {
  description = "The handler for the Lambda function."
  type        = string
  default     = "lambda_function.lambda_handler"
}

variable "timeout" {
  description = "The timeout for the Lambda function in seconds."
  type        = number
  default     = 60

}

variable "memory_size" {
  description = "The memory size for the Lambda function in MB."
  type        = number
  default     = 128
}

variable "runtime" {
  description = "The runtime for the Lambda function."
  type        = string
  default     = "python3.13"
}

variable "lambda_layers" {
  description = "A list of Lambda Layer ARNs to attach to the Lambda function"
  type        = list(string)
  default     = []
}

variable "environment_variables" {
  description = "A map of environment variables to pass to the Lambda function."
  type        = map(string)
  default     = {}
}

# variable "lambda_function_role" {
#   description = "The IAM role for the Lambda function."
#   type        = string
#   default     = aws_iam_role.iam_for_lambda.arn
# }
