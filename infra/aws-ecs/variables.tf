variable "aws_region" { type = string, default = "ap-south-1" }
variable "project_name" { type = string, default = "mediqueue-demo" }
variable "image_uri" {
  type = string
  description = "Full ECR image URI including tag"
}
variable "allowed_cidr" {
  type = string
  default = "0.0.0.0/0"
  description = "Demo only. Restrict this CIDR before use beyond a short demo."
}
