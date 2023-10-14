module "vpc" {
  source   = "./modules/vpc"
  vpc_cidr = "10.8.0.0/16"
  name     = "vpc-app-web"
}

module "subnet-priv-a" {
  source            = "./modules/subnet/private"
  name              = "subnet-priv-a"
  vpc_id            = module.vpc.vpc_id
  subnet_cidr_block = "10.8.1.0/24"
  availability_zone = "us-east-1a"
  depends_on        = [module.vpc]
}

module "subnet-priv-b" {
  source            = "./modules/subnet/private"
  name              = "subnet-priv-b"
  vpc_id            = module.vpc.vpc_id
  subnet_cidr_block = "10.8.2.0/24"
  availability_zone = "us-east-1b"
  depends_on        = [module.vpc]
}

module "subnet-pub-a" {
  source            = "./modules/subnet/public"
  name              = "subnet-pub-a"
  vpc_id            = module.vpc.vpc_id
  subnet_cidr_block = "10.8.3.0/24"
  availability_zone = "us-east-2a"
  depends_on        = [module.vpc]
}

module "subnet-pub-b" {
  source            = "./modules/subnet/public"
  name              = "subnet-pub-a"
  vpc_id            = module.vpc.vpc_id
  subnet_cidr_block = "10.8.4.0/24"
  availability_zone = "us-east-1a"
  depends_on        = [module.vpc]
}

module "routetable-priv-a" {
  source              = "./modules/routetable"
  vpc_id              = module.vpc.vpc_id
  subnet_associations = [module.subnet-priv-a.id]
  routes = [
    {
      destination_cidr_block = "0.0.0.0/0"
      nat_gateway_id         = module.subnet-priv-a.ntgw_id
    },
    {
      destination_cidr_block = module.vpc.vpc_cidr
      gateway_id             = "local"
    }
  ]
}

module "routetable-priv-b" {
  source              = "./modules/routetable"
  vpc_id              = module.vpc.vpc_id
  subnet_associations = [module.subnet-priv-b.id]
  routes = [
    {
      destination_cidr_block = "0.0.0.0/0"
      nat_gateway_id         = module.subnet-priv-b.ntgw_id
    },
    {
      destination_cidr_block = module.vpc.vpc_cidr
      gateway_id             = "local"
    }
  ]
}

module "routetable-pub" {
  source              = "./modules/routetable"
  vpc_id              = module.vpc.vpc_id
  subnet_associations = [module.subnet-pub-a.id, module.subnet-pub-b.id]
  routes = [
    {
      destination_cidr_block = "0.0.0.0"
      gateway_id             = module.vpc.igw_id
    },
    {
      destination_cidr_block = module.vpc.vpc_cidr
      gateway_id             = "local"
    }
  ]
}


module "role_eks" {
  source    = "./modules/iam/roles"
  role_name = "eks-role"
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
    "arn:aws:iam::aws:policy/AmazonEKSServicePolicy",
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
    "arn:aws:iam::aws:policy/AdministratorAccess"
  ]
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
      },
    ]
  })
}

module "eks_sg" {
  source  = "./modules/sg"
  sg_name = "eks-sg"
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
  ingress_sg = [
    {
      description     = "Allow all traffic from eks-sg"
      from_port       = 0
      to_port         = 0
      protocol        = "-1"
      security_groups = [module.eks_sg.sg_id]
    }
  ]
  egress = [
    {
      description = "Allow all traffic to VPC"
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
  ]
  tags = {
    Name = "eks-sg"
  }
  depends_on = [module.vpc]
}

module "eks" {
  source     = "./modules/eks"
  eks_name   = "eks-cluster"
  role_arn   = module.role_eks.arn
  sg = module.eks_sg.sg_id
  subnet_ids = [module.subnet-priv-a.id, module.subnet-priv-b.id]
  depends_on = [module.role_eks]
}
  
