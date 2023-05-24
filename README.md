# App CRUD para estudos

Aplicação para estudar api com CRUD(Create, Read, Update, Delete)

## To Run

```bash
flask run --port=8080
```

or

```
docker build . --tag alissondrs/app-web

docker run --rm --publish 8080:8080 alissondrs/app-web
```

## Usage

```bash

# To Read
curl localhost:8080/read/<id>

# To Create
curl -X POST -H "Content-Type: application/json" -d '{"nome": "<nome>", "idade": <idade>}' http://localhost:8080/create

# To update
curl -X PUT -H "Content-Type: application/json" -d '{"nome": "<nome>", "idade": <idade>}' http://localhost:8080/update/<id>

# To delete
curl -X DELETE localhost:8080/delete/<id>


```