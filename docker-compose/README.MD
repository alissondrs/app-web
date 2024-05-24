<!-- CRIAR REAMDE PARA EXECUTAR O DOCKER COMPOSE -->
# Docker Compose
Este é um exemplo de como executar o docker-compose para subir a aplicação web.

## Pré-requisitos
- Docker
- Docker Compose

## Executando
1. Abra o terminal na pasta `app-web/docker-compose`
2. Execute o comando `docker-compose up -d`


## Usage

```bash

# health check
curl localhost:8080/health


# To Read
curl localhost:8080/user/<id>

# To Create
curl -X POST -H "Content-Type: application/json" -d '{"nome": "<nome>", "idade": <idade>}' http://localhost:8080/user

# To update
curl -X PUT -H "Content-Type: application/json" -d '{"nome": "<nome>", "idade": <idade>}' http://localhost:8080/user/<id>

# To delete
curl -X DELETE localhost:8080/user/<id>


```