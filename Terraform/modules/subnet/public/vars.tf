variable "vpc_id" {
  type = string
}
variable "subnet_cidr_block" {
  type = string
}
variable "availability_zone" {
  type = string
}

variable "name" {
  type = string

}

variable "create_nat_gateway" {
  type        = bool
  default     = false
  description = "Whether this public subnet should host a NAT gateway"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Tags applied to the public subnet and related resources"
}
