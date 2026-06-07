output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "VPC CIDR"
  value       = module.vpc.vpc_cidr
}

output "subnet_priv_a_id" {
  description = "Private subnet A ID"
  value       = module.subnet-priv-a.id
}

output "subnet_priv_b_id" {
  description = "Private subnet B ID"
  value       = module.subnet-priv-b.id
}

output "subnet_pub_a_id" {
  description = "Public subnet A ID"
  value       = module.subnet-pub-a.id
}

output "subnet_pub_b_id" {
  description = "Public subnet B ID"
  value       = module.subnet-pub-b.id
}

output "security_group_id" {
  description = "Security group ID"
  value       = module.security-group-app.id
}
