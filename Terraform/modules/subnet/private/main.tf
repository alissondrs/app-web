resource "aws_subnet" "subnet-priv" {
  vpc_id            = var.vpc_id
  cidr_block        = var.subnet_cidr_block
  availability_zone = var.availability_zone
  tags = merge(var.tags, {
    Name = var.name
  })
}