resource "aws_s3_bucket" "knowledge_base_bucket" {
  bucket = local.KNOWLEDGE_BASE_BUCKET_NAME

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_ownership_controls" "knowledge_base_bucket_ownership" {
  bucket = aws_s3_bucket.knowledge_base_bucket.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}
