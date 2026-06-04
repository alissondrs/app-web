resource "aws_subnet" "subnet-pub" {
  vpc_id                  = var.vpc_id
  cidr_block              = var.subnet_cidr_block
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = true
  tags = merge(var.tags, {
    Name = var.name
  })

}

resource "aws_eip" "eip" {
  count  = var.create_nat_gateway ? 1 : 0
  domain = "vpc"
  tags = merge(var.tags, {
    Name = "${var.name}-eip"
  })
}

resource "aws_nat_gateway" "ntgw" {
  count         = var.create_nat_gateway ? 1 : 0
  allocation_id = aws_eip.eip[count.index].id
  subnet_id     = aws_subnet.subnet-pub.id
  tags = merge(var.tags, {
    Name = "${var.name}-nat"
  })
  depends_on = [aws_eip.eip]
}
