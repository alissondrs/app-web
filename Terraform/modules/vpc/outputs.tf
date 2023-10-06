output "vpc_cidr" {
    value = aws_vpc.main.cidr_block
}

output "vpc_id" {
    value = aws_vpc.main.id
  
}

output "igw_id" {
    value = aws_internet_gateway.igw.id
}