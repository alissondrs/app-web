variable "aws_region" {
  description = "AWS region (LocalStack)"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Base name applied to resources"
  type        = string
  default     = "app-web"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "local"
}

variable "vpc_cidr" {
  description = "CIDR block used by the VPC"
  type        = string
  default     = "10.8.0.0/16"
}
