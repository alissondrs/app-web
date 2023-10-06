resource "aws_subnet" "subnet-pub" {
    vpc_id     = var.vpc_id
    cidr_block = var.subnet_cidr_block
    availability_zone = var.availability_zone
    tags = {
        Name = var.name
    }
  
}

