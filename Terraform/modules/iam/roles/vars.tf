variable "role_name" {
    description = "The name of the IAM role"
    type = string
}

variable "assume_role_policy" {
    description = "The assume role policy"
    type = string
}

variable "managed_policy_arns" {
    description = "The managed policy arns"
    type = list(string)
}