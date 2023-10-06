variable "vpc_cidr" {
  default = "10.10.0.0/16"
}
variable "vpc_enable_dns_hostnames" {
  default = true
}
variable "name" {
  type = string
  default = "vpc"
  
}