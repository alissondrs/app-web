resource "aws_eks_cluster" "eks" {
    name = var.eks_name
    role_arn = var.role_arn
    vpc_config {
        subnet_ids = var.subnet_ids
        security_group_ids = [var.sg]
    }
    tags = {
        Name = var.eks_name
    }
  
}