terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.97.0"
    }
  }
  backend "s3" {
    bucket  = "caristeo-ai-terraform-backend"
    key     = "terraform_state/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region  = "us-east-1"
  profile = "caristeo-ai"
}
