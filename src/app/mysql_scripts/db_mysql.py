import mysql.connector
from mysql.connector import connection
from mysql.connector.errors import Error
import os
import logging

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

def connection_db():
    try:
        db_host = os.getenv("DB_HOST")
        db_user = os.getenv("APP_USER")
        db_password = os.getenv("APP_PASSWORD")
        db_name = os.getenv("DB_NAME")
        db_port = os.getenv("DB_PORT")
        # create connection
        conexao = mysql.connector.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            database=db_name,
            port=db_port,
            auth_plugin='mysql_native_password')
        
        logging.info('Conexão com o banco de dados aberta')
        return conexao
    except mysql.connector.Error as erro:
        logging.error(f'Erro ao conectar com o banco de dados: {erro}')
        return None

connection_db()


