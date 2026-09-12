variable "sg_name" {
  type        = string
  description = "The name of the security group"
}

variable "vpc_id" {
  type        = string
  description = "The VPC ID"
}

variable "ingress" {
  type = list(object({
    description = string,
    from_port   = number,
    to_port     = number,
    protocol    = string,
    cidr_blocks = list(string)
  }))
  default     = []
  description = "Ingress Rules"
}

variable "ingress_security_groups" {
  type = list(object({
    description     = string,
    from_port       = number,
    to_port         = number,
    protocol        = string,
    security_groups = list(string),
    self            = bool
  }))
  default     = []
  description = "Ingress rules that reference security groups or self"
}

variable "egress" {
  type = list(object({
    description = string,
    from_port   = number,
    to_port     = number,
    protocol    = string
    cidr_blocks = list(string)
  }))
  default     = []
  description = "Egress Rules"
}

variable "tags" {
  type        = map(string)
  default     = null
  description = "The tags of resource"
}