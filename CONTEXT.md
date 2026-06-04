# Project Context: app-web

> Arquivo de contexto gerado automaticamente para uso com agentes de IA.
> Projeto de estudo de CRUD com Flask, MySQL, Docker, Kubernetes e stack de observabilidade.

---

## Visão Geral

| Campo          | Valor                                                          |
|----------------|----------------------------------------------------------------|
| **Nome**       | app-web                                                        |
| **Tipo**       | REST API educacional — operações CRUD                          |
| **Linguagem**  | Python 3.10                                                    |
| **Framework**  | Flask 2.3.2                                                    |
| **Banco**      | MySQL (mysql-connector-python, SQL puro — sem ORM)             |
| **Versão App** | 1.0.4 (declarada nos metadados do Prometheus)                  |
| **Imagem Hub** | `alissondrs/app-web` (Docker Hub público)                      |
| **Propósito**  | Aprendizado de CRUD, containerização e observabilidade         |

---

## Estrutura de Diretórios

```
app-web/
├── Dockerfile                          # Build da app Flask, porta 8080
├── README.md                           # Guia principal de uso local, Docker e API
├── CONTEXT.md                          # Este arquivo
├── .gitignore
├── Terraform/                         # Base Terraform para AWS (VPC, subnets, SG, EKS)
│   ├── README.md
│   ├── main.tf
│   ├── provider.tf
│   ├── variables.tf
│   └── modules/
├── src/
│   └── app/
│       ├── app.py                      # Entry point da aplicação
│       ├── script.sh                   # Script de carga/teste de performance
│       ├── requirements.txt            # Dependências Python do backend
│       └── mysql_scripts/
│           ├── db_mysql.py             # Compat wrapper para conexão com MySQL
│           └── mysql.sh                # Script shell para seed do banco
│       └── webapp/
│           ├── __init__.py             # Criação da app, logging, CORS e métricas
│           ├── db.py                   # Conexão e erros de banco
│           ├── repository.py           # Operações SQL
│           ├── routes.py               # Rotas Flask
│           └── validation.py           # Validação de payload
├── tests/
│   └── test_app.py                     # Testes HTTP básicos com unittest
├── docker-compose/
│   ├── .env                            # Variáveis locais da stack
│   ├── .env.example                    # Exemplo de ambiente para compose
│   ├── docker-compose.yml              # Stack local: app, db, prometheus, node-exporter, grafana
│   ├── prometheus.yml                  # Configuração de scraping do Prometheus
│   ├── datasources.yaml                # Datasource Grafana → Prometheus via service discovery
│   ├── dashboards.yaml                 # Provisionamento de dashboards do Grafana
│   ├── dashboard.json                  # Dashboard JSON com 5 painéis
│   ├── initdb/
│   │   └── initi.sql                   # SQL de inicialização do MySQL no compose
│   ├── grafana-storage/                # Dados persistentes do Grafana
│   ├── prometheus-data/                # Dados persistentes do Prometheus
│   └── README.MD                       # Guia da stack local com Docker Compose
└── k8s/
    └── kubernetes/
        ├── app/
        │   ├── configmap.yaml          # ConfigMap da aplicação
        │   ├── deployment.yaml         # Deployment da app 1.0.4
        │   ├── secret.yaml             # Secret com senha da app
        │   └── service.yaml            # Service ClusterIP da app
        ├── cluster/
        │   └── cluster.yaml            # Cluster k3d: 2 servidores + 3 agentes
        ├── mysql/
        │   ├── configmap-initdb.yaml   # SQL de inicialização do MySQL
        │   ├── secret.yaml             # Secret do MySQL
        │   ├── service-headless.yaml   # Headless Service para StatefulSet
        │   ├── service.yaml            # Service ClusterIP do MySQL
        │   └── statefulset.yaml        # StatefulSet MySQL fixado em mysql:5.7.44
        ├── kustomization.yaml          # Entrada única para apply -k
        └── README.MD                   # Guia de deploy local em k3d/k3s
```

---

## Stack Tecnológica

### Backend
| Pacote                          | Versão   | Uso                                    |
|---------------------------------|----------|----------------------------------------|
| Flask                           | 2.3.2    | Framework web                          |
| mysql-connector-python          | 8.0.33   | Driver MySQL (SQL puro)                |
| flask-cors                      | 4.0.0    | CORS habilitado para todas as origens  |
| prometheus-flask-exporter       | 0.23.0   | Exportação de métricas `/metrics`      |
| requests                        | 2.31.0   | Cliente HTTP                           |

### Infraestrutura / Serviços
| Serviço         | Imagem                    | Porta | Função                              |
|-----------------|---------------------------|-------|-------------------------------------|
| app             | alissondrs/app-web:1.0.4  | 8080  | API Flask                           |
| db (compose)    | mysql:5.7                 | 3306  | Banco de dados                      |
| mysql (k8s)     | mysql:5.7.44              | 3306  | Banco de dados (StatefulSet)        |
| prometheus      | prom/prometheus           | 9090  | Coleta de métricas                  |
| node-exporter   | prom/node-exporter        | 9100  | Métricas de sistema                 |
| grafana         | grafana/grafana           | 3000  | Visualização (anon access = Admin)  |

---

## Banco de Dados

**Banco:** `appdb`  
**Tabela:** `usuarios`

```sql
CREATE TABLE usuarios (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    nome  VARCHAR(255),
    idade INT
);
```

**Credenciais padrão** (usadas em todos os ambientes — não use em produção):

| Variável              | Valor      |
|-----------------------|------------|
| `DB_NAME`             | appdb      |
| `APP_USER`            | app-user   |
| `APP_PASSWORD`        | 01senha    |
| `MYSQL_ROOT_PASSWORD` | 01senha    |
| `DB_PORT`             | 3306       |
| `DB_HOST` (compose)   | db         |
| `DB_HOST` (k8s)       | mysql |

**Módulo de conexão principal:** `src/app/webapp/db.py` — função `connection_db()`
- Lê variáveis de ambiente obrigatórias
- Usa `auth_plugin='mysql_native_password'`
- Lança erros explícitos para configuração ausente ou indisponibilidade do banco

**Compatibilidade legada:** `src/app/mysql_scripts/db_mysql.py`
- Reexporta `connection_db` para manter compatibilidade com o layout antigo

---

## API — Endpoints

Base URL: `http://localhost:8080`

| Método   | Rota            | Descrição                        | Sucesso | Erros          |
|----------|-----------------|----------------------------------|---------|----------------|
| `GET`    | `/health`       | Health check                     | 200     | 500            |
| `GET`    | `/user/<id>`    | Buscar usuário por ID            | 200     | 404            |
| `GET`    | `/users/`       | Listar todos os usuários         | 200     | —              |
| `POST`   | `/user/`        | Criar usuário                    | 201     | 400, 409       |
| `PUT`    | `/user/<id>`    | Atualizar usuário                | 200     | 404            |
| `DELETE` | `/user/<id>`    | Deletar usuário                  | 204     | 404            |

**Corpo das requisições POST/PUT:**
```json
{ "nome": "Alice", "idade": 28 }
```

**Endpoint de métricas** (auto-gerado pelo prometheus-flask-exporter):
- `GET /metrics` — formato Prometheus text

---

## Variáveis de Ambiente

Todas lidas pelo `app.py` e `db_mysql.py` via `os.environ`:

| Variável       | Obrigatório | Descrição                         |
|----------------|-------------|-----------------------------------|
| `DB_HOST`      | Sim         | Host do MySQL                     |
| `DB_PORT`      | Sim         | Porta do MySQL                    |
| `DB_NAME`      | Sim         | Nome do banco                     |
| `APP_USER`     | Sim         | Usuário do banco                  |
| `APP_PASSWORD` | Sim         | Senha do banco                    |
| `FLASK_APP`    | Sim         | Configurado no Dockerfile: `/app/app.py` |

---

## Métricas Prometheus

**Endpoint:** `/metrics`  
**Info registrada:** `app_info{version="1.0.4"}`  
**Intervalo de scrape:** 15s (por job), global default 5s

Cada endpoint registra 4 métricas customizadas:
- **Counter** `{endpoint}_total` — total de requisições
- **Gauge** `{endpoint}_status` — status atual
- **Summary** `{endpoint}_summary` — duração (resumo)
- **Histogram** `{endpoint}_histogram` — duração (histograma)

Labels: `status`, `route`, `endpoint`, `method`

---

## Observabilidade — Grafana Dashboard

**Dashboard:** `app-web dash`  
**Refresh:** 30s | **Range:** últimos 5 minutos

| Painel            | Tipo           | Query principal                                                                         |
|-------------------|----------------|-----------------------------------------------------------------------------------------|
| Saturação         | Gauge          | CPU idle + Memory available (node-exporter)                                             |
| Health Check      | Status History | `rate(app_health_check_total{status_code="200"}[1m])`                                  |
| Taxa de sucesso   | Time Series    | `sum(rate(flask_http_request_total{status=~"2.."}[1m])) / sum(rate(...[1m])) * 100`    |
| Latência          | Time Series    | `rate(...duration_seconds_sum[5m]) / rate(...duration_seconds_count[5m])` + p95         |
| Taxa de erros     | Time Series    | `sum(rate(flask_http_request_total{status=~"5.."}[1m])) / sum(rate(...[1m])) * 100`    |

**Datasource Grafana → Prometheus:** `http://prometheus:9090` (service discovery na rede do compose)

---

## Logging

| Campo    | Valor                                                          |
|----------|----------------------------------------------------------------|
| Módulo   | Python `logging`                                               |
| Arquivo  | `app.log` (em `/app/` no container)                            |
| Nível    | `INFO`                                                         |
| Formato  | `%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s` |

Em Docker Compose, o arquivo é montado como volume: `./app.log:/app/app.log`

---

## Docker — Build

**Dockerfile:**
- Base: `python:3.10-slim`
- Workdir: `/app`
- Copia `requirements.txt` antes para melhorar cache de build
- Instala dependências Python e `curl`
- Copia `./src/app` → `/app`
- Porta exposta: `8080`
- Entrypoint: `flask run --host 0.0.0.0 --port 8080`

```bash
# Build
docker build -t alissondrs/app-web:1.0.4 .

# Run (requer banco externo)
docker run \
  -e DB_HOST=... -e DB_PORT=3306 \
  -e APP_USER=app-user -e APP_PASSWORD=01senha \
  -e DB_NAME=appdb \
  --rm -p 8080:8080 alissondrs/app-web:1.0.4
```

---

## Docker Compose

**Arquivo:** `docker-compose/docker-compose.yml`  
**Rede:** `app-net` (bridge, subnet `172.28.0.0/16`)  
**Volume nomeado:** `mysql-data` (persistência MySQL)

```bash
cd docker-compose
cp .env.example .env
docker compose up -d --build

# Portas disponíveis:
# App:          http://localhost:8080
# Prometheus:   http://localhost:9090
# Grafana:      http://localhost:3000
# MySQL:        localhost:3306
# node-exporter: localhost:9100
```

**Health check da app (compose):**
- `curl -f http://localhost:8080/health` | Interval: 3s | Timeout: 1s | Retries: 3

**Melhorias aplicadas no compose:**
- app construída localmente a partir do branch atual
- `depends_on` da app condicionado à saúde do MySQL
- datasource do Grafana usando discovery por nome de serviço

---

## Kubernetes

**Ferramenta de cluster:** k3d (k3s em Docker)

### Cluster (`k8s/kubernetes/cluster/cluster.yaml`)
- API: `k3d.io/v1alpha2`
- Nome: `k8s-cluster`
- Servidores (control plane): 2
- Agentes (workers): 3
- Portas mapeadas: 80:80 e 443:443 → server:0

### App (`k8s/kubernetes/app/`)
- Kind: Deployment | Réplicas: 1
- Imagem: `alissondrs/app-web:1.0.4`
- Configuração não sensível em `ConfigMap`
- Segredo da aplicação em `Secret`
- `startupProbe`, `readinessProbe` e `livenessProbe` em `GET /health`
- Service: `app-web` (ClusterIP, porta 8080)

### MySQL (`k8s/kubernetes/mysql/`)
- Kind: StatefulSet | Réplicas: 1
- Imagem: `mysql:5.7.44`
- PVC: `mysql-data` | ReadWriteOnce | 1Gi
- Headless Service: `mysql-headless`
- Service interno para a app: `mysql`
- Segredos em `Secret`

### Inicialização do banco (k8s)
- ConfigMap `mysql-initdb` com SQL inline:
  ```sql
  USE appdb;
  CREATE TABLE IF NOT EXISTS usuarios (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), idade INT);
  GRANT ALL PRIVILEGES ON appdb.* TO 'app-user'@'%';
  FLUSH PRIVILEGES;
  ```

```bash
# Deploy completo
k3d cluster create --config k8s/kubernetes/cluster/cluster.yaml
kubectl apply -k k8s/kubernetes
kubectl port-forward svc/app-web 8080:8080
```

---

## Terraform

**Pasta:** `Terraform/`

Base Terraform voltada a uma infraestrutura AWS reutilizável para a `app-web` e futuras aplicações.

**Recursos principais:**
- VPC com DNS habilitado
- 2 subnets públicas
- 2 subnets privadas
- 1 NAT Gateway por subnet pública
- Route tables públicas e privadas
- Security group base para EKS
- Cluster EKS com node group gerenciado

**Melhorias aplicadas:**
- `aws_region` e `aws_profile` parametrizados
- seleção de AZs baseada na região configurada
- NAT Gateway movido para as subnets públicas
- correção das IAM roles do EKS (control plane e node group)
- tags de subnet para integração com EKS / load balancers
- tipagem melhor em variáveis e rotas
- lockfile `.terraform.lock.hcl`

**Validação executada:**
```bash
cd Terraform
terraform fmt -recursive
terraform init -backend=false
terraform validate
```

---

## Script de Carga

**Arquivo:** `src/app/script.sh`  
**Uso:** Gerar tráfego contínuo para testar o sistema de monitoramento.

Loop infinito executando:
1. Cria 600 usuários (user9001–user9600) com idades aleatórias
2. Atualiza 480 usuários (user81–user560)
3. Lê 1001 usuários (IDs 4000–5000)
4. Faz requisições para endpoint inexistente (testa 404s)
5. Deleta 151 usuários (IDs 4850–5000)
6. Atualiza mais 1200 usuários (IDs 4001–5200)

---

## Ausências Notáveis

| Categoria          | Status                                                             |
|--------------------|--------------------------------------------------------------------|
| Testes             | ✅ `unittest` com cobertura básica de rotas principais             |
| CI/CD              | ❌ Nenhum pipeline configurado                                     |
| Linting/Formatação | ❌ Sem flake8, pylint, black, etc.                                 |
| Autenticação na API| ❌ Todos os endpoints públicos sem auth                            |
| HTTPS              | ❌ Somente HTTP                                                    |
| ORM                | ❌ SQL puro com mysql-connector-python                             |
| Paginação          | ❌ `/users/` retorna todos os registros                            |
| Migrations         | ❌ Schema gerenciado via scripts SQL avulsos                       |
| Secrets Management | ⚠️ Melhorado no k8s com `Secret`, mas ainda simples no compose/Terraform |
| Frontend           | ❌ Apenas API backend                                              |

---

## Considerações de Segurança

> Este projeto é **educacional** e não deve ser usado em produção sem as devidas correções.

- Credenciais hardcoded em `docker-compose/.env` e manifests Kubernetes
- Sem autenticação na API (qualquer cliente acessa todos os endpoints)
- SQL raw ainda é usado, mas as rotas principais usam parâmetros no mysql-connector
- Grafana com acesso anônimo habilitado e role Admin
- Sem HTTPS em nenhum ambiente
- Imagem Docker pública no Docker Hub

---

## Referência Rápida

```bash
# Testar health check
curl http://localhost:8080/health

# Listar usuários
curl http://localhost:8080/users/

# Criar usuário
curl -X POST http://localhost:8080/user/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Alice", "idade": 28}'

# Buscar por ID
curl http://localhost:8080/user/1

# Atualizar
curl -X PUT http://localhost:8080/user/1 \
  -H "Content-Type: application/json" \
  -d '{"nome": "Alice Updated", "idade": 29}'

# Deletar
curl -X DELETE http://localhost:8080/user/1

# Ver métricas Prometheus
curl http://localhost:8080/metrics
```
