variable "vpc_id" {
    description = "VPC ID"
}
variable "routes" {
    type = list
    default = []
}

variable "subnet_associations" {
  type        = list
  default     = []
}