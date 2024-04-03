# App CRUD para estudos

Aplicação para estudar api com CRUD(Create, Read, Update, Delete)

## To Run

```bash
flask run --port=8080
```
or


```


docker run -e APP_USER=$APP_USER -e DB_HOST=$DB_HOST -e APP_PASSWORD=$APP_PASSWORD -e DB_NAME=$DB_NAME -e DB_PORT=$DB_PORT  --rm --publish 8080:8080 --network=host alissondrs/app-web

```

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