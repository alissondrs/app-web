-- Criação do database
CREATE DATABASE IF NOT EXISTS appdb;

-- O usuário e a senha são criados pelo entrypoint do MySQL a partir do .env.
GRANT ALL PRIVILEGES ON appdb.* TO 'app-user'@'%';
FLUSH PRIVILEGES;

-- Criação da tabela de usuários
USE appdb;
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    idade INT
);
