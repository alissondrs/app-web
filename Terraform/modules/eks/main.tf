resource "aws_eks_cluster" "eks" {
    name = var.eks_name
    role_arn = aws_iam_role.eks.arn
    vpc_config {
        subnet_ids = var.subnet_ids
        security_group_ids = [aws_security_group.eks.id]
    }
    tags = {
        Name = var.eks_name
    }
  
}