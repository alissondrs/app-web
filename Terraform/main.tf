data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  selected_azs = slice(data.aws_availability_zones.available.names, 0, 2)

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  eks_cluster_name = "${var.project_name}-eks"
}

module "vpc" {
  source   = "./modules/vpc"
  vpc_cidr = var.vpc_cidr
  name     = "vpc-${var.project_name}"
  tags     = local.common_tags
}

module "subnet-priv-a" {
  source            = "./modules/subnet/private"
  name              = "${var.project_name}-subnet-priv-a"
  vpc_id            = module.vpc.vpc_id
  subnet_cidr_block = "10.8.1.0/24"
  availability_zone = local.selected_azs[0]
  tags = merge(local.common_tags, {
    Tier                                              = "private"
    "kubernetes.io/cluster/${local.eks_cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"                 = "1"
  })
}

module "subnet-priv-b" {
  source            = "./modules/subnet/private"
  name              = "${var.project_name}-subnet-priv-b"
  vpc_id            = module.vpc.vpc_id
  subnet_cidr_block = "10.8.2.0/24"
  availability_zone = local.selected_azs[1]
  tags = merge(local.common_tags, {
    Tier                                              = "private"
    "kubernetes.io/cluster/${local.eks_cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"                 = "1"
  })
}

module "subnet-pub-a" {
  source             = "./modules/subnet/public"
  name               = "${var.project_name}-subnet-pub-a"
  vpc_id             = module.vpc.vpc_id
  subnet_cidr_block  = "10.8.3.0/24"
  availability_zone  = local.selected_azs[0]
  create_nat_gateway = true
  tags = merge(local.common_tags, {
    Tier                                              = "public"
    "kubernetes.io/cluster/${local.eks_cluster_name}" = "shared"
    "kubernetes.io/role/elb"                          = "1"
  })
}

module "subnet-pub-b" {
  source             = "./modules/subnet/public"
  name               = "${var.project_name}-subnet-pub-b"
  vpc_id             = module.vpc.vpc_id
  subnet_cidr_block  = "10.8.4.0/24"
  availability_zone  = local.selected_azs[1]
  create_nat_gateway = true
  tags = merge(local.common_tags, {
    Tier                                              = "public"
    "kubernetes.io/cluster/${local.eks_cluster_name}" = "shared"
    "kubernetes.io/role/elb"                          = "1"
  })
}

module "routetable-priv-a" {
  source              = "./modules/routetable"
  name                = "${var.project_name}-rt-private-a"
  vpc_id              = module.vpc.vpc_id
  subnet_associations = [module.subnet-priv-a.id]
  routes = [
    {
      destination_cidr_block = "0.0.0.0/0"
      nat_gateway_id         = module.subnet-pub-a.ntgw_id
    }
  ]
  tags = merge(local.common_tags, {
    Tier = "private"
  })
}

module "routetable-priv-b" {
  source              = "./modules/routetable"
  name                = "${var.project_name}-rt-private-b"
  vpc_id              = module.vpc.vpc_id
  subnet_associations = [module.subnet-priv-b.id]
  routes = [
    {
      destination_cidr_block = "0.0.0.0/0"
      nat_gateway_id         = module.subnet-pub-b.ntgw_id
    }
  ]
  tags = merge(local.common_tags, {
    Tier = "private"
  })
}

module "routetable-pub" {
  source              = "./modules/routetable"
  name                = "${var.project_name}-rt-public"
  vpc_id              = module.vpc.vpc_id
  subnet_associations = [module.subnet-pub-a.id, module.subnet-pub-b.id]
  routes = [
    {
      destination_cidr_block = "0.0.0.0/0"
      gateway_id             = module.vpc.igw_id
    }
  ]
  tags = merge(local.common_tags, {
    Tier = "public"
  })
}

module "role_eks" {
  source    = "./modules/iam/roles"
  role_name = "${local.eks_cluster_name}-cluster-role"
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  ]
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "eks.amazonaws.com"
        }
      },
    ]
  })
}

module "security-group-eks" {
  source  = "./modules/sg"
  sg_name = "${local.eks_cluster_name}-sg"
  vpc_id  = module.vpc.vpc_id
  ingress = [
    {
      description = "Allow all traffic from VPC"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = [module.vpc.vpc_cidr]
    }
  ]
  ingress_security_groups = [
    {
      description     = "Allow all traffic within EKS security group"
      from_port       = 0
      to_port         = 0
      protocol        = "-1"
      security_groups = []
      self            = true
    }
  ]
  egress = [
    {
      description = "Allow outbound traffic"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
  ]
  tags = merge(local.common_tags, {
    Name = "${local.eks_cluster_name}-sg"
  })
}

module "eks" {
  source     = "./modules/eks"
  eks_name   = local.eks_cluster_name
  role_arn   = module.role_eks.arn
  sg         = [module.security-group-eks.id]
  subnet_ids = [module.subnet-priv-a.id, module.subnet-priv-b.id]
  tags       = local.common_tags
}


