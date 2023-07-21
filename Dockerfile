FROM python:3.10-slim

ENV APP_USER=app-user
ENV APP_PASSWORD=02senha
ENV DB_NAME=appdb
ENV DB_HOST=127.0.0.1
ENV DB_PORT=3306
ENV FLASK_APP=/app/app.py


COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]