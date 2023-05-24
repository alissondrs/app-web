FROM python:3.8-alpine

RUN pip install \
        flask \
        flask_cors

WORKDIR /app

COPY . .

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]
