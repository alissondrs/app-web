#!/bin/bash

# Variáveis de ambiente para configurações do banco de dados
export DB_USER=""
export DB_PASSWORD=""
export DB_NAME=""

# Criação do banco de dados
mysql -u "$DB_USER" -p"$DB_PASSWORD" -e "CREATE DATABASE $DB_NAME"

# Criação da tabela de usuários
mysql -u "$DB_USER" -p"$DB_PASSWORD" -D "$DB_NAME" -e "CREATE TABLE usuarios (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), idade INT)"

# Lista de nomes aleatórios
nomes=("Alice" "Bob" "Charlie" "David" "Eva" "Frank" "Grace" "Henry" "Ivy" "Jack")

# Inserção dos usuários
for i in {1..10}; do
  nome=${nomes[$RANDOM % ${#nomes[@]}]}
  idade=$((RANDOM % 48 + 18))
  mysql -u "$DB_USER" -p"$DB_PASSWORD" -D "$DB_NAME" -e "INSERT INTO usuarios (nome, idade) VALUES ('$nome', $idade)"
done

echo "Configuração do banco de dados e inserção de usuários concluída com sucesso!"
