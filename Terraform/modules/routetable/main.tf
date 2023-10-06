resource "aws_route_table" "route_table" {
    vpc_id = var.vpc_id

}

resource "aws_route" "route" {
  count = length(var.routes)

  route_table_id = aws_route_table.route_table.id

  destination_cidr_block      = try(var.routes[count.index].destination_cidr_block, null)
  destination_ipv6_cidr_block = try(var.routes[count.index].destination_ipv6_cidr_block, null)
  gateway_id                 = try(var.routes[count.index].gateway_id, null)
  nat_gateway_id             = try(var.routes[count.index].nat_gateway_id, null)
  
  depends_on = [aws_route_table.route_table]
}

resource "aws_route_table_association" "a" {
  count = length(var.subnet_associations)

  route_table_id = aws_route_table.route_table.id
  subnet_id      = var.subnet_associations[count.index]
}