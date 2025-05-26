resource "aws_s3_bucket" "lambda_layer_bucket" {
  bucket_prefix = var.s3_bucket_name_prefix
}

resource "null_resource" "delete_layer_output" {
  triggers = {
    requirements_hash = filemd5(var.requirements_file_path)
  }

  provisioner "local-exec" {
    command     = "if (Test-Path -Path \"./${var.layer_output_path}\") { Remove-Item -Recurse -Force \"./${var.layer_output_path}\" } else { Write-Output \"Directory ./${var.layer_output_path} does not exist, skipping deletion.\" }"
    interpreter = ["powershell", "-Command"]
  }
}

resource "null_resource" "create_layer_dependencies" {
  provisioner "local-exec" {
    command     = "if (Test-Path -Path \"./${var.layer_output_path}\") { Remove-Item -Recurse -Force \"./${var.layer_output_path}\" }; New-Item -Path \"./${var.layer_output_path}/python/lib/python${var.python_version}/site-packages\" -ItemType Directory -Force; uv venv -p ${var.python_version}; uv pip install -p ${var.python_version} --no-build-isolation --python-platform=linux --target=\"./${var.layer_output_path}/python/lib/python${var.python_version}/site-packages\" --python-version ${var.python_version} --only-binary=:all: --upgrade -r ${var.requirements_file_path}"
    interpreter = ["powershell", "-Command"]
  }

  depends_on = [null_resource.delete_layer_output]
  triggers = {
    requirements_hash = filemd5(var.requirements_file_path)
  }
}

resource "null_resource" "create_deployments_dir" {
  provisioner "local-exec" {
    command     = "if (-Not (Test-Path -Path './deployments/requirements/${var.layer_name}-requirement-package')) { New-Item -Path './deployments/requirements/${var.layer_name}-requirement-package' -ItemType Directory -Force }"
    interpreter = ["powershell", "-Command"]
  }
}

data "archive_file" "layer_zip" {
  type        = "zip"
  source_dir  = "./${var.layer_output_path}"
  output_path = "./deployments/requirements/${var.layer_name}-requirement-package/layer.zip"
  depends_on  = [null_resource.create_layer_dependencies, null_resource.create_deployments_dir]
}

resource "aws_s3_object" "lambda_layer_object" {
  bucket     = aws_s3_bucket.lambda_layer_bucket.id
  key        = "layers-${var.layer_name}-${filemd5(var.requirements_file_path)}.zip"
  source     = data.archive_file.layer_zip.output_path
  depends_on = [data.archive_file.layer_zip]
}

resource "aws_lambda_layer_version" "lambda_general_layer" {
  layer_name               = var.layer_name
  s3_bucket                = aws_s3_bucket.lambda_layer_bucket.id
  s3_key                   = aws_s3_object.lambda_layer_object.key
  compatible_runtimes      = var.layer_compatible_runtimes
  compatible_architectures = var.layer_compatible_architectures
  depends_on               = [aws_s3_object.lambda_layer_object]
  
  lifecycle {
    create_before_destroy = true
  }
}
