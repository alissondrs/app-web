resource "aws_iam_role" "role" {
    name = var.role_name
    assume_role_policy = var.assume_role_policy
    managed_policy_arns = var.managed_policy_arns
}

