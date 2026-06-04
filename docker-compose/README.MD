# Docker Compose

Stack local para subir a aplicacao web com MySQL, Prometheus, node-exporter e Grafana.

## Pré-requisitos
- Docker
- Docker Compose plugin

## Executando
1. Copie o arquivo de ambiente:

   ```bash
   cp .env.example .env
   ```

2. Ajuste as senhas em `.env`.

3. Suba a stack:

   ```bash
   docker compose up -d --build
   ```

## Endpoints locais

- App: `http://localhost:8080`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- MySQL: `localhost:3306`
- node-exporter: `http://localhost:9100`

## Usage

```bash

# health check
curl http://localhost:8080/health


# To Read
curl http://localhost:8080/user/<id>

# To Create
curl -X POST -H "Content-Type: application/json" -d '{"nome": "<nome>", "idade": <idade>}' http://localhost:8080/user/

# To update
curl -X PUT -H "Content-Type: application/json" -d '{"nome": "<nome>", "idade": <idade>}' http://localhost:8080/user/<id>

# To delete
curl -X DELETE http://localhost:8080/user/<id>

# To read all
curl http://localhost:8080/users/
```
