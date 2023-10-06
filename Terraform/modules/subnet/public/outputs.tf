output "subnet_cidr" {
    value = aws_subnet.subnet-pub.cidr_block
}

output "id" {
    value = aws_subnet.subnet-pub.id
}
