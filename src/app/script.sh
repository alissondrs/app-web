#!/bin/bash

# Definir o prefixo do nome do usuário
user_prefix="user"

# Loop para criar 30 usuários
for i in {1..30}
do
   username="${user_prefix}${i}"
   idade=$(( ( RANDOM % 100 )  + 1 ))
   curl -X POST -H "Content-Type: application/json" -d '{"nome": "'$username'", "idade": '$idade'}' http://localhost:8080/user/
   echo "Usuário $username $idade criado."
done