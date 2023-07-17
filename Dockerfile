FROM python:3.10-slim





ENV DB_USER=app-user
ENV DB_PASSWORD=02senha
ENV DB_NAME=appdb
ENV DB_HOST=localhost
ENV FLASK_APP /app
WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["flask", "run", "--host" "0.0.0.0", "--port" "8080"]