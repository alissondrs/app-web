## Criar um resource para ec2 com userdata a partir de um secriptshell
resource "aws_instance" "ec2" {
  ami = var.ami
  instance_type = var.instance_type
  subnet_id = var.subnet_id
  security_group_ids = var.security_group_ids
  key_name = var.key_name
  user_data = file(var.userdata)
  tags = {
    Name = var.name
  }
}

