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
 depends_on = [ module.vpc ]
}

module "subnet-priv-b" {
  source            = "./modules/subnet/private"
  name              = "subnet-priv-b"
  vpc_id            = module.vpc.vpc_id
  subnet_cidr_block = "10.8.2.0/24"
  availability_zone = "us-east-1b"
    depends_on = [ module.vpc ]
}

module "subnet-pub-a" {
  source            = "./modules/subnet/public"
  name              = "subnet-pub-a"
  vpc_id            = module.vpc.vpc_id
  subnet_cidr_block = "10.8.3.0/24"
  availability_zone = "us-east-2a"
    depends_on = [ module.vpc ]
}


module "routetable-priv-a" {
    source = "./modules/routetable"
    vpc_id = module.vpc.vpc_id
    subnet_associations = [module.subnet-priv-a.id]
    routes = [
        {
        destination_cidr_block = "0.0.0.0/0"
        nat_gateway_id         = module.subnet-priv-a.ntgw_id
        },
    ]
}

module "routetable-priv-b" {
    source = "./modules/routetable"
    vpc_id = module.vpc.vpc_id
    subnet_associations = [module.subnet-priv-b.id]
    routes = [
        {
        destination_cidr_block = "0.0.0.0/0"
        nat_gateway_id         = module.subnet-priv-b.ntgw_id
        },
    ]
}

module "routetable-pub-a" {
    source = "./modules/routetable"
    vpc_id = module.vpc.vpc_id
    subnet_associations = [module.subnet-pub-a.id]
    routes = [
        {
        destination_cidr_block = "0.0.0.0"
        gateway_id             = module.vpc.igw_id
        }
    ]
}