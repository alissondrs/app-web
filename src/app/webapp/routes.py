import logging
from contextlib import closing

from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics

from .db import DatabaseConfigurationError, DatabaseConnectionError, connection_db
from .repository import (
    create_user,
    delete_user,
    fetch_all_users,
    fetch_user_by_id,
    fetch_user_by_name,
    update_user,
)
from .validation import InvalidUserPayload, parse_user_payload


def _metric_labels() -> dict[str, object]:
    return {
        "status": lambda response: response.status_code if response is not None else "no_response",
        "route": lambda: request.path if request else "no_request",
        "endpoint": lambda: request.endpoint if request else "no_request",
        "method": lambda: request.method if request else "no_request",
    }


def _database_error_response():
    logging.exception("Database operation failed")
    return jsonify({"mensagem": "database unavailable"}), 500


def register_routes(app: Flask, metrics: PrometheusMetrics) -> None:
    labels = _metric_labels()

    @app.route("/health", methods=["GET"], endpoint="health")
    @metrics.counter("app_health_check_total", "Number of health checks", labels=labels)
    @metrics.gauge("app_health_check_status", "Health check status", labels=labels)
    @metrics.summary("app_health_check_summary", "Health check summary", labels=labels)
    @metrics.histogram("app_health_check_histogram", "Health check histogram", labels=labels)
    def health():
        try:
            with closing(connection_db()):
                logging.info("Health check ok")
                return jsonify({"mensagem": "Health check ok"}), 200
        except (DatabaseConfigurationError, DatabaseConnectionError):
            logging.error("Health check failed")
            return jsonify({"mensagem": "Health check failed"}), 500

    @app.route("/user/<int:user_id>", methods=["GET"], endpoint="read")
    @metrics.counter("app_read_user", "Number of read users", labels=labels)
    @metrics.gauge("app_read_user_status", "Read user status", labels=labels)
    @metrics.summary("app_read_user_summary", "Read user summary", labels=labels)
    @metrics.histogram("app_read_user_histogram", "Read user histogram", labels=labels)
    def read(user_id: int):
        try:
            with closing(connection_db()) as connection:
                logging.info("Reading user")
                user = fetch_user_by_id(connection, user_id)
        except (DatabaseConfigurationError, DatabaseConnectionError):
            return _database_error_response()

        if user:
            logging.info("User found")
            return jsonify(user), 200

        logging.error("User not found")
        return jsonify({"mensagem": "user not found"}), 404

    @app.route("/user/", methods=["POST"], endpoint="create")
    @metrics.counter("app_create_user", "Number of create users", labels=labels)
    @metrics.gauge("app_create_user_status", "Create user status", labels=labels)
    @metrics.summary("app_create_user_summary", "Create user summary", labels=labels)
    @metrics.histogram("app_create_user_histogram", "Create user histogram", labels=labels)
    def create():
        try:
            nome, idade = parse_user_payload(request.get_json(silent=True))
        except InvalidUserPayload as exc:
            return jsonify({"mensagem": str(exc)}), 400

        try:
            with closing(connection_db()) as connection:
                existing_user = fetch_user_by_name(connection, nome)
                if existing_user:
                    logging.error("User already exists")
                    return jsonify({"mensagem": "user already exists"}), 409

                logging.info("Creating new user")
                if create_user(connection, nome, idade):
                    logging.info("User created with success")
                    return jsonify({"mensagem": "user created with susses"}), 201
        except (DatabaseConfigurationError, DatabaseConnectionError):
            return _database_error_response()

        logging.error("User not created")
        return jsonify({"mensagem": "user not created"}), 400

    @app.route("/user/<int:user_id>", methods=["DELETE"], endpoint="delete")
    @metrics.counter("app_delete_user", "Number of delete users", labels=labels)
    @metrics.gauge("app_delete_user_status", "Delete user status", labels=labels)
    @metrics.summary("app_delete_user_summary", "Delete user summary", labels=labels)
    @metrics.histogram("app_delete_user_histogram", "Delete user histogram", labels=labels)
    def delete(user_id: int):
        try:
            with closing(connection_db()) as connection:
                user = fetch_user_by_id(connection, user_id)
                if not user:
                    logging.error("User not found")
                    return jsonify({"mensagem": "user not found"}), 404

                delete_user(connection, user_id)
        except (DatabaseConfigurationError, DatabaseConnectionError):
            return _database_error_response()

        logging.info("User deleted with success")
        return jsonify({"mensagem": "User deleted with sucess"}), 204

    @app.route("/user/<int:user_id>", methods=["PUT"], endpoint="update")
    @metrics.counter("app_update_user", "Number of update users", labels=labels)
    @metrics.gauge("app_update_user_status", "Update user status", labels=labels)
    @metrics.summary("app_update_user_summary", "Update user summary", labels=labels)
    @metrics.histogram("app_update_user_histogram", "Update user histogram", labels=labels)
    def update(user_id: int):
        try:
            nome, idade = parse_user_payload(request.get_json(silent=True))
        except InvalidUserPayload as exc:
            return jsonify({"mensagem": str(exc)}), 400

        try:
            with closing(connection_db()) as connection:
                user = fetch_user_by_id(connection, user_id)
                if not user:
                    logging.error("User not found")
                    return jsonify({"mensagem": "user not found"}), 404

                update_user(connection, user_id, nome, idade)
        except (DatabaseConfigurationError, DatabaseConnectionError):
            return _database_error_response()

        logging.info("User updated with success")
        return jsonify({"mensagem": "User updated with sucess"}), 200

    @app.route("/users/", methods=["GET"], endpoint="read_all")
    @metrics.counter("read_all_users", "Number of read all users", labels=labels)
    @metrics.gauge("read_all_users_status", "Read all users status", labels=labels)
    @metrics.summary("read_all_users_summary", "Read all users summary", labels=labels)
    @metrics.histogram("read_all_users_histogram", "Read all users histogram", labels=labels)
    def read_all():
        try:
            with closing(connection_db()) as connection:
                users = fetch_all_users(connection)
        except (DatabaseConfigurationError, DatabaseConnectionError):
            return _database_error_response()

        logging.info("Reading all users")
        return jsonify(users), 200
