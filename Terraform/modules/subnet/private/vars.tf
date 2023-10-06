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
 
variable "vpc" {
  default = true
}
