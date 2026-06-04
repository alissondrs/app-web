output "subnet_cidr" {
  value = aws_subnet.subnet-pub.cidr_block
}

output "id" {
  value = aws_subnet.subnet-pub.id
}

output "ntgw_id" {
  value = try(aws_nat_gateway.ntgw[0].id, null)
}
