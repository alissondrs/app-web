#criar um recurso de vpc
resource "aws_vpc" "main" {
    cidr_block = var.vpc_cidr
    enable_dns_hostnames = var.vpc_enable_dns_hostnames 
}

resource "aws_internet_gateway" "igw" {
    vpc_id = aws_vpc.main.id
    tags = {
        Name = var.name
    }
    depends_on = [ aws_vpc.main ]
  
}

# resource "aws_internet_gateway_attachment" "igw_attach" {
#     vpc_id = aws_vpc.main.id
#     internet_gateway_id = aws_internet_gateway.igw.id
#     depends_on = [ aws_internet_gateway.igw ]
# }