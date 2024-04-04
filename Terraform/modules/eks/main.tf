resource "aws_eks_cluster" "eks" {
    name = var.eks_name
    role_arn = var.role_arn
    enabled_cluster_log_types = var.enabled_cluster_log_types
    vpc_config {
        subnet_ids = var.subnet_ids
        security_group_ids = var.sg
    }
    tags = {
        Name = var.eks_name
    }
  
}

resource "aws_cloudwatch_log_group" "eks" {

  name              = "/aws/eks/${var.eks_name}/cluster"
  retention_in_days = 7


}

data "tls_certificate" "eks" {
  url = aws_eks_cluster.eks.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url             = data.tls_certificate.eks.url
}

data "aws_iam_policy_document" "eks_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:kube-system:aws-node"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "eks" {
  assume_role_policy = data.aws_iam_policy_document.eks_assume_role_policy.json
  name               = "eks"
}


data "aws_ssm_parameter" "eks_ami_release_version" {
  name = "/aws/service/eks/optimized-ami/${aws_eks_cluster.eks.version}/amazon-linux-2/recommended/release_version"
}

resource "aws_eks_node_group" "eks" {
  cluster_name    = aws_eks_cluster.eks.name
  node_group_name = "eks"
  node_role_arn   = aws_iam_role.eks.arn
  subnet_ids      = var.subnet_ids
  version         = aws_eks_cluster.eks.version
  release_version = nonsensitive(data.aws_ssm_parameter.eks_ami_release_version.value)

  scaling_config {
    desired_size = 2
    max_size     = 2
    min_size     = 2
  }
  # depends_on = [aws_eks_addon.eks]
}