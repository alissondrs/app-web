variable "eks_name" {
  description = "The name of the EKS cluster"
  type = string
}

variable "role_arn" {
  description = "The ARN of the IAM role"
  type = string
}

variable "subnet_ids" {
  description = "The subnet IDs"
  type = list(string)
}

variable "sg" {
  description = "The security group ID"
  type = string
}
 