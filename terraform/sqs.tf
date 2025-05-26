resource "aws_sqs_queue" "split_n_convert_pdf_dlq" {
  name = "split_n_convert_pdf_dlq"
}

resource "aws_sqs_queue" "split_n_convert_pdf_queue" {
  name                       = "split_n_convert_pdf_queue"
  delay_seconds              = 5
  max_message_size           = 262144
  message_retention_seconds  = 86400
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 300

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.split_n_convert_pdf_dlq.arn
    maxReceiveCount     = 1
  })
}

data "aws_caller_identity" "current" {}

resource "aws_sqs_queue_policy" "split_n_convert_pdf_queue_policy" {
  queue_url = aws_sqs_queue.split_n_convert_pdf_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowS3ToSendMessages"
        Effect = "Allow"
        Principal = {
          "Service" = "s3.amazonaws.com"
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.split_n_convert_pdf_queue.arn
        Condition = {
          ArnLike = {
            "aws:SourceArn" = aws_s3_bucket.knowledge_base_bucket.arn
          },
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      },
    ]
  })
}

resource "aws_sqs_queue" "page_ocr_dlq" {
  name       = "page_ocr_dlq.fifo"
  fifo_queue = true
}

resource "aws_sqs_queue" "page_ocr_queue" {
  name                        = "page_ocr_queue.fifo"
  fifo_queue                  = true
  delay_seconds               = 0
  max_message_size            = 262144
  message_retention_seconds   = 86400
  receive_wait_time_seconds   = 0
  visibility_timeout_seconds  = 300
  content_based_deduplication = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.page_ocr_dlq.arn
    maxReceiveCount     = 3
  })

  # Limit the number of inflight messages to 1 for strict sequential processing
  # This is enforced by the Lambda event source mapping batch_size and reserved concurrency
}

resource "aws_sqs_queue_policy" "page_ocr_queue_policy" {
  queue_url = aws_sqs_queue.page_ocr_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          "AWS" : data.aws_caller_identity.current.account_id
        }
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.page_ocr_queue.arn
      }
    ]
  })
}

# resource "aws_sqs_queue_redrive_allow_policy" "split_n_convert_pdf_dlq_allow" {
#   queue_url = aws_sqs_queue.split_n_convert_pdf_dlq.id

#   redrive_allow_policy = jsonencode({
#     redrivePermission = "byQueue",
#     sourceQueueArns   = [aws_sqs_queue.split_n_convert_pdf_queue.arn]
#   })
# }

resource "aws_sqs_queue_redrive_allow_policy" "page_ocr_dlq_allow" {
  queue_url = aws_sqs_queue.page_ocr_dlq.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.page_ocr_queue.arn]
  })
}

