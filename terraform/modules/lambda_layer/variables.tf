variable "s3_bucket_name_prefix" {
  description = "The prefix for the S3 bucket name."
  type        = string
  default     = "lambda-layers"
}

variable "layer_name" {
  description = "The name of the Lambda layer."
  type        = string
  default     = "lambda-layer"
}

variable "layer_compatible_runtimes" {
  description = "A list of Lambda runtimes this layer is compatible with."
  type        = list(string)
  default     = ["python3.11"]
}

variable "python_version" {
  description = "Python version to be used in the layer."
  type        = string
  default     = "3.13"

}

variable "layer_compatible_architectures" {
  type        = list(string)
  description = "Lista de arquiteturas compatíveis com a layer"
  default     = ["x86_64", "arm64"]
}

variable "layer_output_path" {
  description = "output path for layer content"
  type        = string
  default     = "deployment-package/venv-layer"
}

variable "requirements_file_path" {
  description = "requirements.txt path"
  type        = string
  # default     = "../src/requirements.txt"
}
