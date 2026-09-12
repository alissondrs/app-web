variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "routes" {
  type = list(object({
    destination_cidr_block      = optional(string)
    destination_ipv6_cidr_block = optional(string)
    gateway_id                  = optional(string)
    nat_gateway_id              = optional(string)
  }))
  default = []
}

variable "subnet_associations" {
  type    = list(string)
  default = []
}

variable "name" {
  type        = string
  description = "Route table name"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Tags applied to the route table"
}