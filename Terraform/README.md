# Terraform AWS base

Base Terraform para uma infraestrutura compartilhada na AWS, reaproveitavel para a `app-web` e para futuras aplicacoes.

## O que esta estruturado aqui

- VPC com DNS habilitado
- 2 subnets publicas em AZs da regiao configurada
- 2 subnets privadas em AZs da regiao configurada
- 1 NAT Gateway por subnet publica
- Route tables separadas para trafego publico e privado
- Security group base para o EKS
- Cluster EKS com node group gerenciado

## Melhorias aplicadas nesta etapa

- regiao e profile agora sao parametrizados
- AZs agora seguem a regiao configurada, sem hardcode inconsistente
- NAT Gateway saiu das subnets privadas e foi para as publicas
- subnets ganharam tags adequadas para uso com EKS/load balancers
- role do control plane do EKS foi corrigida
- node group agora usa role propria com policies necessarias
- SG passou a suportar regra self-referencing
- route table e outros modulos receberam tipagem e tags mais consistentes

## Uso basico

```bash
cd Terraform
terraform init
terraform fmt -recursive
terraform validate
```

## Variaveis principais

- `aws_region`: regiao AWS
- `aws_profile`: profile local da AWS CLI
- `project_name`: nome base dos recursos
- `environment`: nome do ambiente
- `vpc_cidr`: CIDR da VPC

## Observacoes

- o estado remoto ainda nao foi configurado; hoje o backend continua local
- antes de aplicar em AWS real, vale definir backend remoto (S3 + locking) e revisar naming/tags conforme o ambiente alvo
