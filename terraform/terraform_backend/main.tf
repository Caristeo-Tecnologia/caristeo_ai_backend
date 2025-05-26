terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.97.0"
    }
  }
}

provider "aws" {
  region  = "us-east-1"
  profile = "caristeo-ai"
}


resource "aws_s3_bucket" "terraform_backend" {
  bucket = "caristeo-ai-terraform-backend"

  lifecycle {
    prevent_destroy = true
  }
}