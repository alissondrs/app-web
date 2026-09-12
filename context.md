# Project Context: app-web

> Arquivo de contexto gerado para uso com agentes de IA.
> Projeto de estudo de CRUD com Flask, MySQL, Docker, Kubernetes e stack de observabilidade.

---

## Visão Geral

| Campo          | Valor                                                              |
|----------------|--------------------------------------------------------------------|
| **Nome**       | app-web                                                            |
| **Tipo**       | REST API educacional — operações CRUD                              |
| **Linguagem**  | Python 3.10                                                        |
| **Framework**  | Flask 2.3.2                                                        |
| **Banco**      | MySQL (mysql-connector-python, SQL puro — sem ORM)                 |
| **Versão App** | 1.0.4 (declarada em `APP_VERSION` em `webapp/__init__.py`)         |
| **Imagem Hub** | `alissondrs/app-web` (Docker Hub público)                          |
| **CI/CD**      | GitHub Actions para CI/publicação + Harness CD para o ambiente lab |
| **Propósito**  | Aprendizado de CRUD, containerização e observabilidade             |

---

## Estrutura de Diretórios

```
app-web/
├── Dockerfile                              # Build single-stage, python:3.10-slim, porta 8080
├── README.md                               # Docs de uso com exemplos curl (em PT-BR)
├── CONTEXT.md                              # Este arquivo
├── .gitignore
├── .github/workflows/                      # CI e publicação da imagem
├── ci-project.yaml                          # Contrato mínimo de automação
├── deploy/                                  # Manifests e contrato Harness
├── src/
│   └── app/
│       ├── app.py                          # Entrypoint: chama create_app() do pacote webapp
│       ├── requirements.txt                # 6 dependências Python
│       ├── script.sh                       # Script de carga/teste de performance
│       ├── mysql_scripts/
│       │   ├── db_mysql.py                 # Re-exporta connection_db de webapp.db
│       │   └── mysql.sh                    # Script shell para seed do banco
│       └── webapp/                         # Pacote principal da aplicação
│           ├── __init__.py                 # Factory create_app() + logging + métricas
│           ├── db.py                       # connection_db() + exceções customizadas
│           ├── routes.py                   # register_routes() — todos os endpoints Flask
│           ├── repository.py               # Queries SQL (fetch, create, update, delete)
│           └── validation.py               # parse_user_payload() + InvalidUserPayload
├── docker-compose/
│   ├── .env                                # Variáveis de ambiente (credenciais em plaintext)
│   ├── docker-compose.yml                  # 5 serviços: app, db, prometheus, node-exporter, grafana
│   ├── prometheus.yml                      # Configuração de scraping do Prometheus
│   ├── datasources.yaml                    # Datasource Grafana → Prometheus
│   ├── dashboards.yaml                     # Provisionamento de dashboards do Grafana
│   ├── dashboard.json                      # Dashboard JSON com 5 painéis
│   ├── initdb/
│   │   └── initi.sql                       # SQL de inicialização do banco
│   ├── grafana-storage/                    # Dados persistentes do Grafana
│   └── prometheus-data/                    # Dados persistentes do Prometheus
└── k8s/
    └── kubernetes/
        ├── cluster/
        │   └── cluster.yaml                # Cluster k3d: 2 servidores + 3 agentes
        ├── kustomization.yaml              # Kustomize — lista todos os manifests
        ├── app/
        │   ├── deployment.yaml             # Deployment app-web (réplicas: 1)
        │   ├── service.yaml                # Service app-web (ClusterIP :8080)
        │   ├── configmap.yaml              # ConfigMap app-web-config (vars de ambiente)
        │   └── (secret criado fora do Git)
        └── mysql/
            ├── statefulset.yaml            # StatefulSet mysql + PVC 1Gi
            ├── service.yaml                # Service mysql (ClusterIP :3306)
            ├── service-headless.yaml       # Service mysql-headless (headless :3306)
            ├── configmap-initdb.yaml       # ConfigMap mysql-initdb (SQL de init)
            └── (secret criado fora do Git)
```

---

## Stack Tecnológica

### Backend
| Pacote                          | Versão   | Uso                                    |
|---------------------------------|----------|----------------------------------------|
| Flask                           | 3.1.3    | Framework web                          |
| Werkzeug                        | 3.1.6    | WSGI utilities (dependência do Flask)  |
| mysql-connector-python          | 9.1.0    | Driver MySQL (SQL puro)                |
| flask-cors                      | 6.0.0    | CORS habilitado para todas as origens  |
| prometheus-flask-exporter       | 0.23.0   | Exportação de métricas `/metrics`      |
| requests                        | 2.33.0   | Cliente HTTP                           |

### Infraestrutura / Serviços
| Serviço         | Imagem                      | Porta | Função                              |
|-----------------|-----------------------------|-------|-------------------------------------|
| app (compose)   | alissondrs/app-web:local    | 8080  | API Flask (build local)             |
| app (k8s)       | alissondrs/app-web:1.0.4    | 8080  | API Flask                           |
| db (compose)    | mysql:5.7                   | 3306  | Banco de dados                      |
| mysql (k8s)     | mysql:5.7.44                | 3306  | Banco de dados (StatefulSet)        |
| prometheus      | prom/prometheus             | 9090  | Coleta de métricas                  |
| node-exporter   | prom/node-exporter          | 9100  | Métricas de sistema                 |
| grafana         | grafana/grafana             | 3000  | Visualização (anon access = Admin)  |

---

## Estrutura Interna do Código (pacote `webapp/`)

O `app.py` é apenas um entrypoint que chama `create_app()`. Toda a lógica está no pacote `src/app/webapp/`:

| Arquivo           | Responsabilidade                                                                 |
|-------------------|----------------------------------------------------------------------------------|
| `__init__.py`     | `create_app()` — configura logging, CORS, PrometheusMetrics e registra rotas     |
| `db.py`           | `connection_db()` — conecta ao MySQL; lança `DatabaseConfigurationError` ou `DatabaseConnectionError` em falha |
| `routes.py`       | `register_routes(app, metrics)` — define todos os endpoints com decorators de métricas |
| `repository.py`   | Funções SQL: `fetch_user_by_id`, `fetch_user_by_name`, `create_user`, `update_user`, `delete_user`, `fetch_all_users` |
| `validation.py`   | `parse_user_payload(payload)` — valida e retorna `(nome, idade)`; lança `InvalidUserPayload` |

> `mysql_scripts/db_mysql.py` apenas re-exporta `connection_db` de `webapp.db`.

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

**Queries SQL** (todas em `repository.py` usando `%s` — prepared statements via mysql-connector):
- `SELECT * FROM usuarios WHERE id = %s`
- `SELECT * FROM usuarios WHERE nome = %s`
- `INSERT INTO usuarios (nome, idade) VALUES (%s, %s)`
- `UPDATE usuarios SET nome = %s, idade = %s WHERE id = %s`
- `DELETE FROM usuarios WHERE id = %s`
- `SELECT * FROM usuarios`

**Credenciais padrão** (não use em produção):

| Variável              | Valor      |
|-----------------------|------------|
| `DB_NAME`             | appdb      |
| `APP_USER`            | app-user   |
| `APP_PASSWORD`        | 01senha    |
| `MYSQL_ROOT_PASSWORD` | 01senha    |
| `DB_PORT`             | 3306       |
| `DB_HOST` (compose)   | db         |
| `DB_HOST` (k8s)       | mysql      |

---

## API — Endpoints

Base URL: `http://localhost:8080`

| Método   | Rota             | Endpoint Flask | Descrição                        | Sucesso | Erros          |
|----------|------------------|----------------|----------------------------------|---------|----------------|
| `GET`    | `/health`        | `health`       | Health check (abre conexão DB)   | 200     | 500            |
| `GET`    | `/user/<id>`     | `read`         | Buscar usuário por ID            | 200     | 404, 500       |
| `GET`    | `/users/`        | `read_all`     | Listar todos os usuários         | 200     | 500            |
| `POST`   | `/user/`         | `create`       | Criar usuário                    | 201     | 400, 409, 500  |
| `PUT`    | `/user/<id>`     | `update`       | Atualizar usuário                | 200     | 400, 404, 500  |
| `DELETE` | `/user/<id>`     | `delete`       | Deletar usuário                  | 204     | 404, 500       |

**Corpo das requisições POST/PUT:**
```json
{ "nome": "Alice", "idade": 28 }
```

**Validação** (via `validation.py`): `nome` deve ser string não-vazia; `idade` deve ser convertível para `int`. Payload inválido retorna 400.

**Endpoint de métricas** (auto-gerado):
- `GET /metrics` — formato Prometheus text

---

## Variáveis de Ambiente

Todas lidas via `os.getenv()` em `webapp/db.py`. Ausência lança `DatabaseConfigurationError`.

| Variável       | Obrigatório | Descrição                              |
|----------------|-------------|----------------------------------------|
| `DB_HOST`      | Sim         | Host do MySQL                          |
| `DB_PORT`      | Sim         | Porta do MySQL                         |
| `DB_NAME`      | Sim         | Nome do banco                          |
| `APP_USER`     | Sim         | Usuário do banco                       |
| `APP_PASSWORD` | Sim         | Senha do banco                         |
| `FLASK_APP`    | Sim         | Configurado no Dockerfile: `/app/app.py` |

---

## Métricas Prometheus

**Endpoint:** `/metrics` | **Group by:** `endpoint`  
**Info registrada:** `app_info{version="1.0.4"}`  
**Intervalo de scrape:** 15s por job, 5s global default

Cada endpoint registra 4 métricas (nomes reais definidos em `routes.py`):

| Endpoint Flask | Counter                  | Gauge                       | Summary                    | Histogram                    |
|----------------|--------------------------|-----------------------------|----------------------------|------------------------------|
| `health`       | `app_health_check_total` | `app_health_check_status`   | `app_health_check_summary` | `app_health_check_histogram` |
| `read`         | `app_read_user`          | `app_read_user_status`      | `app_read_user_summary`    | `app_read_user_histogram`    |
| `create`       | `app_create_user`        | `app_create_user_status`    | `app_create_user_summary`  | `app_create_user_histogram`  |
| `update`       | `app_update_user`        | `app_update_user_status`    | `app_update_user_summary`  | `app_update_user_histogram`  |
| `delete`       | `app_delete_user`        | `app_delete_user_status`    | `app_delete_user_summary`  | `app_delete_user_histogram`  |
| `read_all`     | `read_all_users`         | `read_all_users_status`     | `read_all_users_summary`   | `read_all_users_histogram`   |

Labels por métrica: `status`, `route`, `endpoint`, `method`

---

## Observabilidade — Grafana Dashboard

**Dashboard:** `app-web dash` | **Refresh:** 30s | **Range:** últimos 5 minutos

| Painel            | Tipo           | Query principal                                                                         |
|-------------------|----------------|-----------------------------------------------------------------------------------------|
| Saturação         | Gauge          | CPU idle + Memory available (node-exporter)                                             |
| Health Check      | Status History | `rate(app_health_check_total{status_code="200"}[1m])`                                  |
| Taxa de sucesso   | Time Series    | `sum(rate(flask_http_request_total{status=~"2.."}[1m])) / sum(rate(...[1m])) * 100`    |
| Latência          | Time Series    | `rate(...duration_seconds_sum[5m]) / rate(...duration_seconds_count[5m])` + p95         |
| Taxa de erros     | Time Series    | `sum(rate(flask_http_request_total{status=~"5.."}[1m])) / sum(rate(...[1m])) * 100`    |

**Datasource Grafana → Prometheus:** `http://prometheus:9090` (por nome de serviço na rede Docker)

---

## Logging

| Campo    | Valor                                                                  |
|----------|------------------------------------------------------------------------|
| Módulo   | Python `logging` (configurado em `webapp/__init__.py::configure_logging`) |
| Arquivo  | `app.log` (relativo ao CWD `/app` no container)                        |
| Nível    | `INFO`                                                                 |
| Formato  | `%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s`      |

Em Docker Compose, o arquivo é montado como volume: `./app.log:/app/app.log`

---

## Docker — Build

**Dockerfile** (single-stage):
- Base: `python:3.10-slim`
- Workdir: `/app`
- Instala `requirements.txt` de `/tmp/` antes de copiar o código
- Instala `curl` via apt-get
- Copia: `./src/app` → `/app`
- Porta exposta: `8080`
- Entrypoint: `flask run --host 0.0.0.0 --port 8080`
- Env extras: `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`

```bash
# Build
docker build -t alissondrs/app-web .

# Run (requer banco externo)
docker run \
  -e DB_HOST=... -e DB_PORT=3306 \
  -e APP_USER=app-user -e APP_PASSWORD=01senha \
  -e DB_NAME=appdb \
  --rm -p 8080:8080 alissondrs/app-web
```

---

## Docker Compose

**Arquivo:** `docker-compose/docker-compose.yml`  
**Rede:** `app-net` (bridge, subnet `172.28.0.0/16`)  
**Volume nomeado:** `mysql-data` (persistência MySQL)

**Serviços:**

| Serviço       | Imagem                       | Porta | Notas                                    |
|---------------|------------------------------|-------|------------------------------------------|
| `db`          | mysql:5.7                    | 3306  | healthcheck com mysqladmin ping          |
| `prometheus`  | prom/prometheus              | 9090  | IP estático `172.28.1.2` na rede         |
| `node-exporter`| prom/node-exporter          | 9100  | —                                        |
| `grafana`     | grafana/grafana              | 3000  | Anon login habilitado, role Admin        |
| `app`         | alissondrs/app-web:local     | 8080  | Build local, depends_on db (healthy)     |

**Health checks:**
- `db`: `mysqladmin ping -h 127.0.0.1 -uroot` | Interval: 5s | Timeout: 3s | Retries: 15 | Start: 15s
- `app`: `curl -f http://localhost:8080/health` | Interval: 3s | Timeout: 1s | Retries: 3

```bash
cd docker-compose
docker-compose up -d

# Portas disponíveis:
# App:           http://localhost:8080
# Prometheus:    http://localhost:9090
# Grafana:       http://localhost:3000
# MySQL:         localhost:3306
# node-exporter: localhost:9100
```

---

## Kubernetes

**Ferramenta de cluster:** k3d (k3s em Docker)  
**Deploy via:** Kustomize (`k8s/kubernetes/kustomization.yaml`)

### Cluster (`k8s/kubernetes/cluster/cluster.yaml`)
- API: `k3d.io/v1alpha2` | Nome: `k8s-cluster`
- Servidores (control plane): 2 | Agentes (workers): 3
- Portas mapeadas: `80:80` e `443:443` → server:0

### App (`k8s/kubernetes/app/`)

**Deployment** (`deployment.yaml`):
- Nome: `app-web` | Réplicas: 1
- Imagem: `alissondrs/app-web:1.0.4` | `imagePullPolicy: IfNotPresent`
- Vars de ambiente: via `configMapRef: app-web-config` + `secretKeyRef: app-web-secrets` (APP_PASSWORD)
- startupProbe: `GET /health` | failureThreshold: 20 | period: 5s
- readinessProbe: `GET /health` | initialDelay: 5s | period: 10s | timeout: 2s
- livenessProbe: `GET /health` | initialDelay: 15s | period: 20s | timeout: 2s
- Resources: requests `100m/128Mi` | limits `300m/256Mi`

**Service** (`service.yaml`): `app-web` | ClusterIP | porta 8080

**ConfigMap** (`configmap.yaml`): `app-web-config`
```
DB_HOST: mysql
DB_PORT: "3306"
DB_NAME: appdb
APP_USER: app-user
```

**Secret:** `app-web-secrets`, criado fora do repositório pelo Harness ou pelo
operador do cluster.

### MySQL (`k8s/kubernetes/mysql/`)

**StatefulSet** (`statefulset.yaml`):
- Nome: `mysql` | serviceName: `mysql-headless` | Réplicas: 1
- Imagem: `mysql:5.7.44` | `imagePullPolicy: IfNotPresent`
- Secrets: `mysql-secrets` (MYSQL_ROOT_PASSWORD, MYSQL_PASSWORD)
- PVC: `mysql-data` | ReadWriteOnce | 1Gi
- ConfigMap montado em `/docker-entrypoint-initdb.d`
- startupProbe/readiness/liveness: tcpSocket porta 3306
- Resources: requests `100m/256Mi` | limits `500m/512Mi`

**Services:**
- `mysql` (`service.yaml`): ClusterIP | porta 3306 (acesso interno)
- `mysql-headless` (`service-headless.yaml`): headless (`clusterIP: None`) | porta 3306

**ConfigMap** (`configmap-initdb.yaml`): `mysql-initdb` com `init.sql`:
```sql
USE appdb;
CREATE TABLE IF NOT EXISTS usuarios (...);
GRANT ALL PRIVILEGES ON appdb.* TO 'app-user'@'%';
FLUSH PRIVILEGES;
```

**Secret:** `mysql-secrets`, criado fora do repositório pelo Harness ou pelo
operador do cluster.

```bash
# Deploy completo via Kustomize
k3d cluster create app-web --config k8s/kubernetes/cluster/cluster.yaml
kubectl apply -k k8s/kubernetes/
kubectl port-forward svc/app-web 8080:8080
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
| Testes             | ❌ Nenhum (sem pytest, unittest, etc.)                             |
| CI/CD              | ✅ GitHub Actions + Harness CD documentados e configurados no piloto |
| Linting/Formatação | ❌ Sem flake8, pylint, black, etc.                                 |
| Autenticação na API| ❌ Todos os endpoints públicos sem auth                            |
| HTTPS              | ❌ Somente HTTP                                                    |
| ORM                | ❌ SQL puro com mysql-connector-python                             |
| Paginação          | ❌ `/users/` retorna todos os registros                            |
| Migrations         | ❌ Schema gerenciado via scripts SQL avulsos                       |
| Frontend           | ❌ Apenas API backend                                              |

---

## Considerações de Segurança

> Este projeto é **educacional** e não deve ser usado em produção sem as devidas correções.

- Credenciais em plaintext em `docker-compose/.env` e nos Secrets k8s (`stringData`)
- Sem autenticação na API
- Grafana com acesso anônimo habilitado e role Admin
- Sem HTTPS em nenhum ambiente
- Imagem Docker pública no Docker Hub
- SQL injection mitigado: repository usa prepared statements (`%s` via mysql-connector)

---

## Referência Rápida

```bash
# Health check
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
