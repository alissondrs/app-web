import logging

from flask import Flask
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

from .routes import register_routes


LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s"
LOG_DATE_FORMAT = "%d/%m/%Y %I:%M:%S %p"
APP_VERSION = "1.0.3"


def configure_logging() -> None:
    logging.basicConfig(
        filename="app.log",
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
    )


def create_app() -> Flask:
    configure_logging()

    app = Flask(__name__)
    CORS(app)

    metrics = PrometheusMetrics(app, group_by="endpoint")
    metrics.info("app_info", "App Information", version=APP_VERSION)

    register_routes(app, metrics)
    return app
