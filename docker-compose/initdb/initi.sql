-- Criação do database
CREATE DATABASE IF NOT EXISTS appdb;

-- Criação do usuário e concessão de privilégios
CREATE USER 'app-user'@'%' IDENTIFIED BY '01senha';
GRANT ALL PRIVILEGES ON *.* TO 'app-user'@'%';
FLUSH PRIVILEGES;

-- Criação da tabela de usuários
USE DATABASE appdb;
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    idade INT
);

