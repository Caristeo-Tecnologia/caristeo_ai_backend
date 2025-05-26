module "page_ocr_lambda_layer_module" {
  source = "./modules/lambda_layer"

  layer_name                = local.PAGE_OCR_FN_NAME
  s3_bucket_name_prefix     = local.PAGE_OCR_FN_NAME
  layer_output_path         = "${local.LAYERS_OUTPUT_FOLDER_NAME}/${local.PAGE_OCR_LAMBDA_LAYER_NAME}"
  requirements_file_path    = local.PAGE_OCR_LAMBDA_LAYER_REQUIREMENTS_PATH
  python_version            = local.envs["PYTHON_VERSION"]
  layer_compatible_runtimes = ["python3.13"]
}

module "page_ocr_lambda_function_module" {
  source = "./modules/lambda_function"

  lambda_function_name = local.PAGE_OCR_FN_NAME
  lambda_source_dir    = local.PAGE_OCR_LAMBDA_FOLDER_PATH
  lambda_output_path   = local.LAMBDAS_OUTPUT_FOLDER_NAME
  timeout              = 120
  memory_size          = 512


  lambda_layers = [
    module.page_ocr_lambda_layer_module.general_layer_arn,
  ]
}

module "split_n_convert_pdf_lambda_layer_module" {
  source = "./modules/lambda_layer"

  layer_name                = local.SPLIT_N_CONVERT_PDF_LAMBDA_LAYER_NAME
  s3_bucket_name_prefix     = local.SPLIT_N_CONVERT_PDF_LAMBDA_LAYER_NAME
  layer_output_path         = "${local.LAYERS_OUTPUT_FOLDER_NAME}/${local.SPLIT_N_CONVERT_PDF_LAMBDA_LAYER_NAME}"
  requirements_file_path    = local.SPLIT_N_CONVERT_PDF_LAMBDA_LAYER_REQUIREMENTS_PATH
  python_version            = local.envs["PYTHON_VERSION"]
  layer_compatible_runtimes = ["python3.13"]
}

module "split_n_convert_pdf_lambda_function_module" {
  source = "./modules/lambda_function"

  lambda_function_name = local.SPLIT_N_CONVERT_PDF_FN_NAME
  lambda_source_dir    = local.SPLIT_N_CONVERT_PDF_LAMBDA_FOLDER_PATH
  lambda_output_path   = local.LAMBDAS_OUTPUT_FOLDER_NAME
  timeout              = 900
  memory_size          = 512

  lambda_layers = [
    module.split_n_convert_pdf_lambda_layer_module.general_layer_arn,
  ]

  environment_variables = {
    PAGE_OCR_SQS_QUEUE_URL = aws_sqs_queue.page_ocr_queue.id
  }
}

# Configure SQS trigger for Lambda
resource "aws_lambda_event_source_mapping" "split_n_convert_pdf_sqs_lambda_trigger" {
  event_source_arn = aws_sqs_queue.split_n_convert_pdf_queue.arn
  function_name    = module.split_n_convert_pdf_lambda_function_module.abstract_lambda_function_name
  batch_size       = 1
}

# Configure S3 to send notifications to SQS
resource "aws_s3_bucket_notification" "s3_to_sqs_notification" {
  bucket = local.KNOWLEDGE_BASE_BUCKET_NAME

  queue {
    queue_arn     = aws_sqs_queue.split_n_convert_pdf_queue.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "books/"
    filter_suffix = ".pdf"
  }

  depends_on = [aws_sqs_queue_policy.split_n_convert_pdf_queue_policy]
}

# policy for s3 put document 
resource "aws_iam_role_policy_attachment" "s3_trigger" {
  policy_arn = aws_iam_policy.s3_lambda.arn
  role       = module.split_n_convert_pdf_lambda_function_module.abstract_lambda_role_name
}

# Attach the policy to the page_ocr_lambda_function role
resource "aws_iam_role_policy_attachment" "page_ocr_lambda" {
  policy_arn = aws_iam_policy.page_ocr_lambda.arn
  role       = module.page_ocr_lambda_function_module.abstract_lambda_role_name
}


# Configure SQS trigger for page_ocr Lambda
resource "aws_lambda_event_source_mapping" "page_ocr_sqs_trigger" {
  event_source_arn = aws_sqs_queue.page_ocr_queue.arn
  function_name    = module.page_ocr_lambda_function_module.abstract_lambda_function_name
  batch_size       = 1

  scaling_config {
    maximum_concurrency = 3
  }
}

# Add permission for split_n_convert_pdf lambda to send messages to page_ocr_queue
resource "aws_iam_role_policy_attachment" "sqs_send_message_attachment" {
  policy_arn = aws_iam_policy.sqs_send_message_policy.arn
  role       = module.split_n_convert_pdf_lambda_function_module.abstract_lambda_role_name
}
