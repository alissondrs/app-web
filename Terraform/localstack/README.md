# Terraform com LocalStack — Lab Local AWS

Documentacao do processo de provisionamento local de infraestrutura AWS usando **LocalStack** como emulador e **Terraform** como ferramenta de IaC.

Este overlay e um subconjunto do `Terraform/` principal, voltado para validacao e experimentacao local sem necessidade de conta AWS real.

---

## Recursos provisionados

| Recurso                | Quantidade | Descricao                                |
|------------------------|------------|------------------------------------------|
| VPC                    | 1          | Rede principal com DNS habilitado        |
| Internet Gateway       | 1          | Saida publica de internet                |
| Subnets publicas       | 2          | us-east-1a e us-east-1b                  |
| Subnets privadas       | 2          | us-east-1a e us-east-1b                  |
| Elastic IPs            | 2          | Alocados para os NAT Gateways            |
| NAT Gateways           | 2          | Um por subnet publica                    |
| Route Tables           | 3          | Publica (via IGW) e privadas (via NAT)   |
| Route Table Assocs.    | 4          | Associacoes subnet/route table           |
| Security Group         | 1          | Regras basicas ingress/egress            |
| IAM Role               | 1          | Role de exemplo para instancias EC2      |

> EKS foi intencionalmente excluido deste overlay. O cluster EKS nao e suportado de forma completa no LocalStack Community e exige recursos que nao sao necessarios para validacao de rede.

---

## Pre-requisitos

- [Docker](https://docs.docker.com/engine/install/) (via **Colima** no macOS)
- [LocalStack CLI](https://docs.localstack.cloud/getting-started/installation/)
- [Terraform >= 1.5.0](https://developer.hashicorp.com/terraform/install)
- Conta LocalStack com `LOCALSTACK_AUTH_TOKEN` configurado

### Instalacao do LocalStack CLI (macOS)

```bash
brew install localstack/tap/localstack-cli
```

---

## Configuracao do token LocalStack

Configure o token de autenticacao **uma vez** no seu terminal:

```bash
localstack auth set-token
```

Ou persista no shell:

```bash
echo "export LOCALSTACK_AUTH_TOKEN='SEU_TOKEN'" >> ~/.zshrc
source ~/.zshrc
```

> Nunca commite o token em arquivos versionados.

---

## Iniciando o ambiente

### 1. Subir o Docker (Colima no macOS)

```bash
colima start --runtime docker
```

### 2. Iniciar o LocalStack

```bash
localstack start -d
```

Aguarde alguns segundos e valide:

```bash
localstack status
curl http://localhost:4566/_localstack/health
```

O health deve retornar um JSON listando os servicos disponiveis (ec2, iam, sts...).

---

## Provisionando com Terraform

### 1. Entrar na pasta do overlay local

```bash
cd Terraform/localstack
```

### 2. Inicializar o Terraform

```bash
terraform init
```

### 3. Visualizar o plano

```bash
terraform plan
```

Deve mostrar **22 recursos** a criar na primeira execucao.

### 4. Aplicar

```bash
terraform apply
```

Ou aprovando automaticamente:

```bash
terraform apply -auto-approve
```

### 5. Ver os outputs

```bash
terraform output
```

Exemplo de saida esperada:

```
security_group_id = "sg-xxxxxxxxxxxx"
subnet_priv_a_id  = "subnet-xxxxxxxxxxxx"
subnet_priv_b_id  = "subnet-xxxxxxxxxxxx"
subnet_pub_a_id   = "subnet-xxxxxxxxxxxx"
subnet_pub_b_id   = "subnet-xxxxxxxxxxxx"
vpc_cidr          = "10.8.0.0/16"
vpc_id            = "vpc-xxxxxxxxxxxx"
```

---

## Inspecionando recursos criados

Com o `awslocal` (wrapper do AWS CLI para LocalStack):

```bash
# Instalar awslocal
pip install awscli-local

# Listar VPCs
awslocal ec2 describe-vpcs

# Listar subnets
awslocal ec2 describe-subnets

# Listar NAT Gateways
awslocal ec2 describe-nat-gateways

# Listar route tables
awslocal ec2 describe-route-tables

# Listar security groups
awslocal ec2 describe-security-groups

# Listar IAM roles
awslocal iam list-roles
```

Ou usando AWS CLI diretamente com endpoint local:

```bash
aws --endpoint-url=http://localhost:4566 ec2 describe-vpcs
```

---

## Destruindo os recursos

```bash
cd Terraform/localstack
terraform destroy -auto-approve
```

---

## Parando o ambiente

```bash
localstack stop
colima stop
```

---

## Diferencas entre este overlay e o Terraform principal

| Aspecto              | `Terraform/` (AWS real)          | `Terraform/localstack/` (lab)        |
|----------------------|-----------------------------------|---------------------------------------|
| Provider endpoint    | AWS real                          | `http://localhost:4566`               |
| Credenciais          | Profile AWS CLI real              | `access_key = "test"` (mock)          |
| AZs                  | Detectadas dinamicamente          | Hardcoded `us-east-1a/b`             |
| EKS                  | Sim (cluster + node group)        | Nao (excluido)                        |
| State backend        | Local (a migrar para S3)          | Local                                 |
| Ambiente             | `sa-east-1` (producao futura)     | `us-east-1` (LocalStack default)      |

---

## Proximos passos sugeridos

- Adicionar modulo RDS/MySQL para testar banco de dados local
- Configurar S3 + DynamoDB para backend remoto de state no LocalStack
- Adicionar ECR local para hospedar a imagem `alissondrs/app-web:1.0.4`
- Criar pipeline de CI que valide o Terraform com `localstack` antes de qualquer apply real
