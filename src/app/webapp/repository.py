from contextlib import closing
from typing import Any

from mysql.connector import MySQLConnection


def _serialize_user(row: tuple[Any, ...] | None) -> dict[str, Any] | None:
    if row is None:
        return None

    return {
        "id": row[0],
        "nome": row[1],
        "idade": row[2],
    }


def fetch_user_by_id(connection: MySQLConnection, user_id: int) -> dict[str, Any] | None:
    with closing(connection.cursor()) as cursor:
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
        return _serialize_user(cursor.fetchone())


def fetch_user_by_name(connection: MySQLConnection, nome: str) -> dict[str, Any] | None:
    with closing(connection.cursor()) as cursor:
        cursor.execute("SELECT * FROM usuarios WHERE nome = %s", (nome,))
        return _serialize_user(cursor.fetchone())


def create_user(connection: MySQLConnection, nome: str, idade: int) -> bool:
    with closing(connection.cursor()) as cursor:
        cursor.execute(
            "INSERT INTO usuarios (nome, idade) VALUES (%s, %s)",
            (nome, idade),
        )
        connection.commit()
        return cursor.rowcount == 1


def update_user(connection: MySQLConnection, user_id: int, nome: str, idade: int) -> None:
    with closing(connection.cursor()) as cursor:
        cursor.execute(
            "UPDATE usuarios SET nome = %s, idade = %s WHERE id = %s",
            (nome, idade, user_id),
        )
        connection.commit()


def delete_user(connection: MySQLConnection, user_id: int) -> None:
    with closing(connection.cursor()) as cursor:
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
        connection.commit()


def fetch_all_users(connection: MySQLConnection) -> list[dict[str, Any]]:
    with closing(connection.cursor()) as cursor:
        cursor.execute("SELECT * FROM usuarios")
        return [_serialize_user(row) for row in cursor.fetchall()]
