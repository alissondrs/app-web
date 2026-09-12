locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  azs = ["${var.aws_region}a", "${var.aws_region}b"]
}

module "vpc" {
  source   = "../modules/vpc"
  vpc_cidr = var.vpc_cidr
  name     = "vpc-${var.project_name}"
  tags     = local.common_tags
}

module "subnet-priv-a" {
  source            = "../modules/subnet/private"
  name              = "${var.project_name}-subnet-priv-a"
  vpc_id            = module.vpc.vpc_id
  subnet_cidr_block = "10.8.1.0/24"
  availability_zone = local.azs[0]
  tags = merge(local.common_tags, {
    Tier = "private"
  })
}

module "subnet-priv-b" {
  source            = "../modules/subnet/private"
  name              = "${var.project_name}-subnet-priv-b"
  vpc_id            = module.vpc.vpc_id
  subnet_cidr_block = "10.8.2.0/24"
  availability_zone = local.azs[1]
  tags = merge(local.common_tags, {
    Tier = "private"
  })
}

module "subnet-pub-a" {
  source             = "../modules/subnet/public"
  name               = "${var.project_name}-subnet-pub-a"
  vpc_id             = module.vpc.vpc_id
  subnet_cidr_block  = "10.8.3.0/24"
  availability_zone  = local.azs[0]
  create_nat_gateway = true
  tags = merge(local.common_tags, {
    Tier = "public"
  })
}

module "subnet-pub-b" {
  source             = "../modules/subnet/public"
  name               = "${var.project_name}-subnet-pub-b"
  vpc_id             = module.vpc.vpc_id
  subnet_cidr_block  = "10.8.4.0/24"
  availability_zone  = local.azs[1]
  create_nat_gateway = true
  tags = merge(local.common_tags, {
    Tier = "public"
  })
}

module "routetable-priv-a" {
  source              = "../modules/routetable"
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
  source              = "../modules/routetable"
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
  source              = "../modules/routetable"
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

module "security-group-app" {
  source  = "../modules/sg"
  sg_name = "${var.project_name}-sg"
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
      description     = "Allow all traffic within security group"
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
    Name = "${var.project_name}-sg"
  })
}

module "iam-role-app" {
  source    = "../modules/iam/roles"
  role_name = "${var.project_name}-role"
  managed_policy_arns = []
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}
