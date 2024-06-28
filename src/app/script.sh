#!/bin/bash

# Definir o prefixo do nome do usuário
user_prefix="user"

# Loop para criar 30 usuários
for i in {900..2000}
do
   username="${user_prefix}${i}"
   idade=$(( ( RANDOM % 100 )  + 1 ))
   curl -X POST -H "Content-Type: application/json" -d '{"nome": "'$username'", "idade": '$idade'}' http://localhost:8080/user/
   echo "Usuário $username $idade criado."
done

for i in {100..1000}
do
   curl localhost:8080/user/$i
done


for i in {50..300}
do
   curl -X DELETE localhost:8080/user/$i
done
