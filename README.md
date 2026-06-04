# App CRUD para estudos

Aplicacao Flask para estudar CRUD, containerizacao e observabilidade com MySQL.

## Estrutura

O backend foi organizado em modulos menores:

- `src/app/app.py`: ponto de entrada da aplicacao
- `src/app/webapp/`: criacao da app, rotas, validacao e acesso ao banco
- `src/app/mysql_scripts/`: scripts auxiliares legados do MySQL
- `tests/`: validacoes HTTP da API
- `docker-compose/`: stack local com MySQL, Prometheus e Grafana
- `k8s/kubernetes/`: manifests para k3d/k3s com `kustomization.yaml`
- `Terraform/`: base Terraform para AWS (VPC, subnets, SG e EKS)

## Rodando localmente

Crie um ambiente virtual e instale as dependencias:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r src/app/requirements.txt
export FLASK_APP=src/app/app.py
flask run --port=8080
```

> A aplicacao precisa das variaveis `DB_HOST`, `DB_PORT`, `DB_NAME`, `APP_USER` e `APP_PASSWORD`.

## Validacao

```bash
. .venv/bin/activate
python -m unittest discover -s tests -p 'test_*.py'
```

## Docker

```bash
docker build . --tag alissondrs/app-web:1.0.4

docker run \
  -e APP_USER="$APP_USER" \
  -e DB_HOST="$DB_HOST" \
  -e APP_PASSWORD="$APP_PASSWORD" \
  -e DB_NAME="$DB_NAME" \
  -e DB_PORT="$DB_PORT" \
  --rm \
  --publish 8080:8080 \
  --network=host \
  alissondrs/app-web:1.0.4
```

Para subir a stack local com MySQL, Prometheus e Grafana:

```bash
cp docker-compose/.env.example docker-compose/.env
docker compose -f docker-compose/docker-compose.yml up -d --build
```

## Uso

```bash
# health check
curl http://localhost:8080/health

# To Read
curl http://localhost:8080/user/<id>

# To Create
curl -X POST -H "Content-Type: application/json" \
  -d '{"nome": "<nome>", "idade": <idade>}' \
  http://localhost:8080/user/

# To update
curl -X PUT -H "Content-Type: application/json" \
  -d '{"nome": "<nome>", "idade": <idade>}' \
  http://localhost:8080/user/<id>

# To delete
curl -X DELETE http://localhost:8080/user/<id>

# To read all
curl http://localhost:8080/users/
```
