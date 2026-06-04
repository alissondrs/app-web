variable "aws_region" {
  description = "AWS region for shared infrastructure"
  type        = string
  default     = "sa-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile used by Terraform"
  type        = string
  default     = "alissondrs"
}

variable "project_name" {
  description = "Base name applied to shared infrastructure resources"
  type        = string
  default     = "app-web"
}

variable "environment" {
  description = "Environment name used in tags"
  type        = string
  default     = "lab"
}

variable "vpc_cidr" {
  description = "CIDR block used by the shared VPC"
  type        = string
  default     = "10.8.0.0/16"
}
