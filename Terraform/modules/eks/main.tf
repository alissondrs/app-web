resource "aws_eks_cluster" "eks" {
  name                      = var.eks_name
  role_arn                  = var.role_arn
  enabled_cluster_log_types = var.enabled_cluster_log_types
  vpc_config {
    subnet_ids              = var.subnet_ids
    security_group_ids      = var.sg
    endpoint_private_access = true
    endpoint_public_access  = true
  }
  tags = merge(var.tags, {
    Name = var.eks_name
  })
  depends_on = [aws_cloudwatch_log_group.eks]
}

resource "aws_cloudwatch_log_group" "eks" {

  name              = "/aws/eks/${var.eks_name}/cluster"
  retention_in_days = 7
  tags = merge(var.tags, {
    Name = var.eks_name
  })

}

data "tls_certificate" "eks" {
  url = aws_eks_cluster.eks.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url             = data.tls_certificate.eks.url
}

data "aws_iam_policy_document" "node_group_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"

    principals {
      identifiers = ["ec2.amazonaws.com"]
      type        = "Service"
    }
  }
}

resource "aws_iam_role" "node_group" {
  assume_role_policy = data.aws_iam_policy_document.node_group_assume_role_policy.json
  name               = "${var.eks_name}-node-group-role"
  tags = merge(var.tags, {
    Name = "${var.eks_name}-node-group-role"
  })
}

resource "aws_iam_role_policy_attachment" "node_group_worker_policy" {
  role       = aws_iam_role.node_group.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "node_group_ecr_policy" {
  role       = aws_iam_role.node_group.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "node_group_cni_policy" {
  role       = aws_iam_role.node_group.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}


data "aws_ssm_parameter" "eks_ami_release_version" {
  name = "/aws/service/eks/optimized-ami/${aws_eks_cluster.eks.version}/amazon-linux-2/recommended/release_version"
}

resource "aws_eks_node_group" "eks" {
  cluster_name    = aws_eks_cluster.eks.name
  node_group_name = "${var.eks_name}-nodes"
  node_role_arn   = aws_iam_role.node_group.arn
  subnet_ids      = var.subnet_ids
  version         = aws_eks_cluster.eks.version
  release_version = nonsensitive(data.aws_ssm_parameter.eks_ami_release_version.value)

  scaling_config {
    desired_size = var.node_group_desired_size
    max_size     = var.node_group_max_size
    min_size     = var.node_group_min_size
  }

  tags = merge(var.tags, {
    Name = "${var.eks_name}-nodes"
  })

  depends_on = [
    aws_iam_role_policy_attachment.node_group_worker_policy,
    aws_iam_role_policy_attachment.node_group_ecr_policy,
    aws_iam_role_policy_attachment.node_group_cni_policy
  ]
}