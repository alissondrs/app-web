import mysql.connector
from mysql.connector import connection
from mysql.connector.errors import Error
import os

def connection_db():
    try:
        db_host = os.getenv("DB_HOST")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")
        
        # create connection
        conexao = mysql.connector.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            database=db_name,
            auth_plugin='mysql_native_password')
        
        
        return conexao
    except mysql.connector.Error as erro:
        print(f"Erro ao abrir conexão com o banco de dados: {erro}")
        return None

connection_db()


