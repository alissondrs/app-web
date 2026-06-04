#!/bin/bash

# Definir o prefixo do nome do usuário
user_prefix="user"




# Loop para criar 30 usuários
while true; do
  for i in {9001..9600}; do
     username="${user_prefix}${i}"
     idade=$(( ( RANDOM % 100 )  + 1 ))
     curl -X POST -H "Content-Type: application/json" -d '{"nome": "'$username'", "idade": '$idade'}' http://localhost:8080/user/
     echo "Usuário $username $idade criado."
  done

  for i in {81..560}; do
     username="${user_prefix}${i}"
     idade=$(( ( RANDOM % 100 )  + 1 ))
     curl -X PUT -H "Content-Type: application/json" -d '{"nome": "'$username'", "idade": '$idade'}' http://localhost:8080/user/$i
     echo "Usuário $username $idade criado."
  done

  for i in {4000..5000}; do
     curl localhost:8080/user/$i
  done

  for i in {3111..5600}; do
     curl localhost:8080/userss/$i
  done

  for i in {4850..5000}; do
     curl -X DELETE localhost:8080/user/$i
  done

  for i in {4001..5200}; do
     username="${user_prefix}${i}"
     idade=$(( ( RANDOM % 100 )  + 1 ))
     curl -X PUT -H "Content-Type: application/json" -d '{"nome": "'$username'", "idade": '$idade'}' http://localhost:8080/user/$i
     echo "Usuário $username $idade criado."
  done
done

# sum by (status_code) (
#   sum_over_time(app_read_user_total[5m]) or 
#   sum_over_time(app_create_user_total[5m]) or 
#   sum_over_time(app_delete_user_total[5m]) or 
#   sum_over_time(app_update_user_total[5m]) or 
#   sum_over_time(read_all_users_total[5m])
# )