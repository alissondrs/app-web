FROM python:3.10-slim

ENV APP_USER=${APP_USER}
ENV APP_PASSWORD=${APP_PASSWORD}
ENV DB_NAME=${DB_NAME}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV FLASK_APP=/app/app.py


COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]

