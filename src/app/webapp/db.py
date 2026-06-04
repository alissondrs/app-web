import logging
import os

import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.errors import Error


class DatabaseConfigurationError(RuntimeError):
    """Raised when required database settings are missing."""


class DatabaseConnectionError(RuntimeError):
    """Raised when a database connection cannot be created."""


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise DatabaseConfigurationError(f"missing required environment variable: {name}")


def connection_db() -> MySQLConnection:
    try:
        connection = mysql.connector.connect(
            user=_get_required_env("APP_USER"),
            password=_get_required_env("APP_PASSWORD"),
            host=_get_required_env("DB_HOST"),
            database=_get_required_env("DB_NAME"),
            port=_get_required_env("DB_PORT"),
            auth_plugin="mysql_native_password",
        )
    except DatabaseConfigurationError:
        logging.exception("Database configuration is incomplete")
        raise
    except Error as exc:
        logging.error("Erro ao conectar com o banco de dados: %s", exc)
        raise DatabaseConnectionError("database unavailable") from exc

    logging.info("Conexão com o banco de dados aberta")
    return connection
