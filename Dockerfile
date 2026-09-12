FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=/app/app.py

COPY ./src/app/requirements.txt /tmp/requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY ./src/app /app

EXPOSE 8080

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]
