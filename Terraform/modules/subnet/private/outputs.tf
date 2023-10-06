output "subnet_cidr" {
    value = aws_subnet.subnet-priv.cidr_block
}

output "id" {
    value = aws_subnet.subnet-priv.id
}

output "ntgw_id" {
    value = aws_nat_gateway.ntgw.id
}
    