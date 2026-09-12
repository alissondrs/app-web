variable "eks_name" {
  description = "The name of the EKS cluster"
  type        = string
}

variable "role_arn" {
  description = "The ARN of the IAM role"
  type        = string
}

variable "subnet_ids" {
  description = "The subnet IDs"
  type        = list(string)
}

variable "sg" {
  description = "The security group ID"
  type        = list(string)
}

variable "enabled_cluster_log_types" {
  default = ["api", "audit"]
  type    = list(string)
}

variable "node_group_desired_size" {
  type        = number
  default     = 2
  description = "Desired number of worker nodes"
}

variable "node_group_min_size" {
  type        = number
  default     = 2
  description = "Minimum number of worker nodes"
}

variable "node_group_max_size" {
  type        = number
  default     = 4
  description = "Maximum number of worker nodes"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Tags applied to EKS resources"
}
