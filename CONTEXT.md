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
├── Dockerfile                          # Build single-stage, python:3.10-slim, porta 8080
├── README.md                           # Docs de uso com exemplos curl (em PT-BR)
├── CONTEXT.md                          # Este arquivo
├── .gitignore
├── src/
│   └── app/
│       ├── app.py                      # Aplicação Flask principal (~170 linhas)
│       ├── requirements.txt            # 5 dependências Python
│       ├── script.sh                   # Script de carga/teste de performance
│       └── mysql_scripts/
│           ├── db_mysql.py             # Módulo de conexão com MySQL
│           └── mysql.sh                # Script shell para seed do banco
├── docker-compose/
│   ├── .env                            # Variáveis de ambiente (credenciais em plaintext)
│   ├── docker-compose.yml              # 5 serviços: app, db, prometheus, node-exporter, grafana
│   ├── prometheus.yml                  # Configuração de scraping do Prometheus
│   ├── datasources.yaml                # Datasource Grafana → Prometheus
│   ├── dashboards.yaml                 # Provisionamento de dashboards do Grafana
│   ├── dashboard.json                  # Dashboard JSON com 5 painéis
│   ├── initdb/
│   │   └── initi.sql                   # SQL de inicialização do banco
│   ├── grafana-storage/                # Dados persistentes do Grafana
│   └── prometheus-data/                # Dados persistentes do Prometheus
└── k8s/
    └── kubernetes/
        ├── cluster/
        │   └── cluster.yaml            # Cluster k3d: 2 servidores + 3 agentes
        ├── deployment/
        │   └── app-web.yaml            # Deployment + Service (ClusterIP :8080)
        └── statefulsets/
            └── mysql/
                ├── mysql.yaml          # StatefulSet + Service headless + PVC 1Gi
                └── initdb.yaml         # ConfigMap com SQL de inicialização
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
| app             | alissondrs/app-web        | 8080  | API Flask                           |
| db (compose)    | mysql:5.7                 | 3306  | Banco de dados                      |
| mysql (k8s)     | mysql:latest              | 3306  | Banco de dados (StatefulSet)        |
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
| `DB_HOST` (k8s)       | mysql-service.default |

**Módulo de conexão:** `src/app/mysql_scripts/db_mysql.py` — função `connection_db()`
- Lê variáveis de ambiente
- `auth_plugin='mysql_native_password'` (hardcoded)
- Retorna `None` em caso de erro (logado em `app.log`)

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

**Datasource Grafana → Prometheus:** IP estático `http://172.28.1.2:9090` (rede Docker compose)

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

**Dockerfile** (single-stage):
- Base: `python:3.10-slim`
- Workdir: `/app`
- Copia: `./src/app` → `/app`
- Instala: `pip install -r requirements.txt` + `curl` (apt-get)
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

**Arquivo:** `docker-compose/docker-compose.yml` (versão 3.9)  
**Rede:** `app-net` (bridge, subnet `172.28.0.0/16`)  
**Volume nomeado:** `mysql-data` (persistência MySQL)

```bash
cd docker-compose
docker-compose up -d

# Portas disponíveis:
# App:          http://localhost:8080
# Prometheus:   http://localhost:9090
# Grafana:      http://localhost:3000
# MySQL:        localhost:3306
# node-exporter: localhost:9100
```

**Health check da app (compose):**
- `curl -f http://localhost:8080/health` | Interval: 3s | Timeout: 1s | Retries: 3

> ⚠️ Atenção: serviço Prometheus declarado como `proemtheus` no compose (typo no nome do serviço).

---

## Kubernetes

**Ferramenta de cluster:** k3d (k3s em Docker)

### Cluster (`k8s/kubernetes/cluster/cluster.yaml`)
- API: `k3d.io/v1alpha2`
- Nome: `k8s-cluster`
- Servidores (control plane): 2
- Agentes (workers): 3
- Portas mapeadas: 80:80 e 443:443 → server:0

### App Deployment (`k8s/kubernetes/deployment/app-web.yaml`)
- Kind: Deployment | Réplicas: 1
- Imagem: `alissondrs/app-web:1.0.4`
- Porta: 8080
- Liveness + Readiness Probe: `GET /health` | initialDelay: 30s | period: 10s
- Service: ClusterIP na porta 8080

### MySQL StatefulSet (`k8s/kubernetes/statefulsets/mysql/mysql.yaml`)
- Kind: StatefulSet | Réplicas: 1
- Imagem: `mysql:latest`
- PVC: `mysql-persistent-storage` | ReadWriteOnce | 1Gi
- Service: Headless (`clusterIP: None`) | Porta 3306
- Nome do serviço: `mysql-service` (DNS: `mysql-service.default`)

### Inicialização do banco (k8s)
- ConfigMap `initdb` com SQL inline:
  ```sql
  USE appdb;
  CREATE TABLE usuarios (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), idade INT);
  CREATE USER 'app-user'@'%' IDENTIFIED BY '01senha';
  GRANT ALL PRIVILEGES ON *.* TO 'app-user'@'%';
  FLUSH PRIVILEGES;
  ```

```bash
# Deploy completo
k3d cluster create app-web --config k8s/kubernetes/cluster/cluster.yaml
kubectl apply -f k8s/kubernetes/statefulsets/mysql/initdb.yaml
kubectl apply -f k8s/kubernetes/statefulsets/mysql/mysql.yaml
kubectl apply -f k8s/kubernetes/deployment/app-web.yaml
kubectl port-forward svc/app-web-service 8080:8080
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
| CI/CD              | ❌ Nenhum pipeline configurado                                     |
| Linting/Formatação | ❌ Sem flake8, pylint, black, etc.                                 |
| Autenticação na API| ❌ Todos os endpoints públicos sem auth                            |
| HTTPS              | ❌ Somente HTTP                                                    |
| ORM                | ❌ SQL puro com mysql-connector-python                             |
| Paginação          | ❌ `/users/` retorna todos os registros                            |
| Migrations         | ❌ Schema gerenciado via scripts SQL avulsos                       |
| Secrets Management | ⚠️ Credenciais em plaintext no `.env` e manifests k8s            |
| Frontend           | ❌ Apenas API backend                                              |

---

## Considerações de Segurança

> Este projeto é **educacional** e não deve ser usado em produção sem as devidas correções.

- Credenciais hardcoded em `docker-compose/.env` e manifests Kubernetes
- Sem autenticação na API (qualquer cliente acessa todos os endpoints)
- Risco de SQL injection (queries raw sem prepared statements em alguns pontos)
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
