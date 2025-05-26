# # Define the permissions needed for each IAM role
# locals {
#   lambda_roles = {
#     "s3_textract" = {
#       statements = [
#         {
#           Effect   = "Allow"
#           Action   = ["s3:GetObject", "s3:PutObject"]
#           Resource = "arn:aws:s3:::${local.envs["BUCKET_NAME"]}/*"
#         },
#         {
#           Effect = "Allow"
#           Action = ["s3:ListBucket"]
#           Resource = ["arn:aws:s3:::${local.envs["BUCKET_NAME"]}"]
#         },
#         {
#           Effect   = "Allow"
#           Action   = ["textract:*"]
#           Resource = "*"
#         },
#         {
#           Effect  = "Allow"
#           Action = ["sqs:*"]
#           Resource = "*"
#         },
#         {
#           Effect = "Allow"
#           Action = ["lambda:InvokeFunction"]
#           Resource  = "*"
#         },
#         {
#           Effect   = "Allow"
#           Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
#           Resource = "arn:aws:logs:*:*:*"
#         }
#       ]
#     },
#     "s3_bedrock" = {
#       statements = [
#         {
#           Effect   = "Allow"
#           Action   = ["s3:GetObject", "s3:PutObject"]
#           Resource = ["arn:aws:s3:::${local.envs["BUCKET_NAME"]}/*"]
#         },
#         {
#           Effect   = "Allow"
#           Action   = ["bedrock:InvokeModel"]
#           Resource = "*"
#         },
#         {
#           Effect = "Allow"
#           Action = ["s3:ListBucket"]
#           Resource = ["arn:aws:s3:::${local.envs["BUCKET_NAME"]}"]
#         },
#         {
#           Effect   = "Allow"
#           Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
#           Resource = "arn:aws:logs:*:*:*"
#         }
#       ]
#     },

#     "s3_textract_bedrock" = {
#       statements = [
#         {
#           Effect   = "Allow"
#           Action   = ["s3:GetObject", "s3:PutObject"]
#           Resource = ["arn:aws:s3:::${local.envs["BUCKET_NAME"]}/*"]
#         },
#         {
#           Effect = "Allow"
#           Action = ["s3:ListBucket"]
#           Resource = ["arn:aws:s3:::${local.envs["BUCKET_NAME"]}"]
#         },
#         {
#           Effect   = "Allow"
#           Action   = ["textract:*"]
#           Resource = "*"
#         },
#         {
#           Effect   = "Allow"
#           Action   = ["bedrock:InvokeModel"]
#           Resource = "*"
#         },
#         {
#           Effect  = "Allow"
#           Action = ["sqs:*"]
#           Resource = "*"
#         },
#         {
#           Effect   = "Allow"
#           Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
#           Resource = "arn:aws:logs:*:*:*"
#         },
#         {
#           Effect   = "Allow"
#           Action   = ["lambda:InvokeFunction"]
#           Resource = "*"
#         }
#       ]
#     }
#     "s3_only" = {
#       statements = [
#         {
#           Effect   = "Allow"
#           Action   = ["s3:GetObject", "s3:PutObject"]
#           Resource = "arn:aws:s3:::${local.envs["BUCKET_NAME"]}/*"
#         },
#         {
#           Effect = "Allow"
#           Action = ["s3:ListBucket"]
#           Resource = ["arn:aws:s3:::${local.envs["BUCKET_NAME"]}"]
#         },
#         {
#           Effect   = "Allow"
#           Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
#           Resource = "arn:aws:logs:*:*:*"
#         }
#       ]
#     }

#     "s3_sqs" = {
#       statements = [
#         {
#           Effect   = "Allow"
#           Action   = ["s3:GetObject", "s3:PutObject"]
#           Resource = "arn:aws:s3:::${local.envs["BUCKET_NAME"]}/*"
#         },
#         {
#           Effect = "Allow"
#           Action = ["s3:ListBucket"]
#           Resource = ["arn:aws:s3:::${local.envs["BUCKET_NAME"]}"]
#         },
#         {
#           Effect = "Allow"
#           Action = ["sqs:*"]
#           Resource = "*"
#         },
#         {
#           Effect   = "Allow"
#           Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
#           Resource = "arn:aws:logs:*:*:*"
#         }
#       ]
#     }
#   }
# }

# # Create IAM roles and corresponding policies
# resource "aws_iam_role" "lambda_roles" {
#   for_each = local.lambda_roles

#   name = "${local.envs["LAMBDA_ROLE_NAME"]}_${each.key}"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [{
#       Effect = "Allow",
#       Principal = {
#         Service = "lambda.amazonaws.com"
#       },
#       Action = "sts:AssumeRole"
#     }]
#   })
# }

# resource "aws_iam_policy" "lambda_policies" {
#   for_each = local.lambda_roles

#   name = "${local.envs["LAMBDA_ROLE_NAME"]}_${each.key}_policy"

#   policy = jsonencode({
#     Version   = "2012-10-17",
#     Statement = local.lambda_roles[each.key].statements
#   })
# }

# # Attach policies to corresponding IAM roles
# resource "aws_iam_role_policy_attachment" "lambda_role_attachments" {
#   for_each = local.lambda_roles

#   role       = aws_iam_role.lambda_roles[each.key].name
#   policy_arn = aws_iam_policy.lambda_policies[each.key].arn
# }

# IAM roles and policies for AWS services

# Textract publish role for SNS
# resource "aws_iam_role" "textract_publish_role" {
#   name = "TextractPublishRole"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Effect = "Allow"
#       Principal = {
#         Service = "textract.amazonaws.com"
#       }
#       Action = "sts:AssumeRole"
#     }]
#   })
# }

# # Policy to allow Amazon Textract to publish to SNS topic
# resource "aws_iam_policy" "textract_sns_publish_policy" {
#   name        = "TextractSNSPublishPolicy"
#   description = "Policy to allow Amazon Textract to publish to SNS topic"

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Effect   = "Allow"
#       Action   = "sns:Publish"
#       Resource = "*" # Using * for now, can be replaced with specific SNS topic ARN when available
#     }]
#   })
# }

# S3 Lambda policy document
data "aws_iam_policy_document" "s3_lambda" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = ["arn:aws:s3:::${local.KNOWLEDGE_BASE_BUCKET_NAME}/*"]
  }

  statement {
    effect    = "Allow"
    actions   = ["bedrock:InvokeModel"]
    resources = ["*"]
  }

  statement {
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::${local.KNOWLEDGE_BASE_BUCKET_NAME}"]
  }

  statement {
    effect    = "Allow"
    actions   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:ChangeMessageVisibility"
    ]
    resources = [aws_sqs_queue.split_n_convert_pdf_queue.arn, aws_sqs_queue.page_ocr_queue.arn]
  }
}

# S3 Lambda IAM policy
resource "aws_iam_policy" "s3_lambda" {
  name   = "${local.SPLIT_N_CONVERT_PDF_FN_NAME}-policy"
  policy = data.aws_iam_policy_document.s3_lambda.json
}

# Page OCR Lambda IAM policy
resource "aws_iam_policy" "page_ocr_lambda" {
  name   = "${local.PAGE_OCR_FN_NAME}-policy"
  policy = data.aws_iam_policy_document.s3_lambda.json
}

# Policy to allow split_n_convert_pdf Lambda to send messages to page_ocr_queue
resource "aws_iam_policy" "sqs_send_message_policy" {
  name        = "split_n_convert_pdf_send_page_ocr_queue"
  description = "Allow split_n_convert_pdf Lambda to send messages to page_ocr_queue"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["sqs:SendMessage"]
        Resource = aws_sqs_queue.page_ocr_queue.arn
      }
    ]
  })
}
