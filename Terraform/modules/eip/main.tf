resource "aws_eip" "eip" {
    vpc = var.vpc
    tags = {
        Name = var.name
    }
  
}




