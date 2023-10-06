resource "aws_subnet" "subnet-priv" {
    vpc_id     = var.vpc_id
    cidr_block = var.subnet_cidr_block
    availability_zone = var.availability_zone
    tags = {
        Name = var.name
    }
  
}

resource "aws_eip" "eip" {
    vpc = var.vpc
    tags = {
        Name = var.name
    }
  depends_on = [ aws_subnet.subnet-priv ]
}

resource "aws_nat_gateway" "ntgw" {
    allocation_id = aws_eip.eip.id
    subnet_id = aws_subnet.subnet-priv.id
    tags = {
        Name = var.name
    }
  depends_on = [ aws_eip.eip ]
}