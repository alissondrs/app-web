from flask import Flask, jsonify, request
import json
from flask_cors import CORS
from mysql_scripts.db_mysql import connection_db
import logging
from prometheus_flask_exporter import PrometheusMetrics

# Configurar o logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
app = Flask(__name__)
CORS(app)
metrics = PrometheusMetrics(app)

@app.route('/health', methods=['GET'])
@metrics.do_not_track()
@metrics.counter('health_check', 'Number of health checks')
def health():
    #validar conexção com o banco de dados
    db = connection_db()
    if db:
        logging.info('Health check ok')
        return jsonify({'mensagem': 'Health check ok'}), 200
    else:
        logging.error('Health check failed')
        return jsonify({'mensagem': 'Health check failed'}), 500
    
#Read route
@app.route('/user/<int:id>', methods=['GET'])
@metrics.do_not_track()
@metrics.counter('read_user', 'Number of read users')
def read(id):
    db = connection_db()
    cursor = db.cursor()
    logging.info('Reading user')
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    user = cursor.fetchone()

    if user:
        user_data = {
            'id': user[0],
            'nome': user[1],
            'idade': user[2]  
        }
        logging.info('User found')
        return jsonify(user_data), 200
    else:
        logging.error('User not found')
        return jsonify({'mensagem': 'user not found'}), 404
     
@app.route('/user/', methods=['POST'])
@metrics.do_not_track()
@metrics.counter('create_user', 'Number of create users')
def create():
    db = connection_db()
    cursor = db.cursor()
    new_user = request.json
    nome = new_user.get('nome')
    idade = new_user.get('idade')
    #verify if user already exists
    cursor.execute("SELECT * FROM usuarios WHERE nome = %s", (nome,))
    user = cursor.fetchone()
    if user:
        logging.error('User already exists')
        return jsonify({'mensagem': 'user already exists'}), 409
    #create new user
    logging.info('Creating new user')
    cursor.execute("INSERT INTO usuarios (nome, idade) VALUES (%s, %s)", (nome, idade))
    db.commit()
    #verify if new user was created
    if cursor.rowcount == 1:
        logging.info('User created with success')
        return jsonify({'mensagem': 'user created with susses'}), 201
    else:
        logging.error('User not created')
        return jsonify({'mensagem': 'user not created'}), 400

@app.route('/user/<int:id>', methods=['DELETE'])
@metrics.do_not_track()
@metrics.counter('delete_user', 'Number of delete users')
def delete(id):
    db = connection_db()
    cursor = db.cursor()
    #verify if user exists
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    user = cursor.fetchone()
    if not user:
        logging.error('User not found')
        return jsonify({'mensagem': 'user not found'}), 404
    # delete user
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    db.commit()
    logging.info('User deleted with success')
    return jsonify({'mensagem': 'User deleted with sucess'}), 200

@app.route('/user/<int:id>', methods=['PUT'])
@metrics.do_not_track()
@metrics.counter('update_user', 'Number of update users')
def update(id):
    db = connection_db()
    cursor = db.cursor()
    #verify if user exists
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    user = cursor.fetchone()
    if not user:
        logging.error('User not found')
        return jsonify({'mensagem': 'user not found'}), 404
    #update user
    new_user = request.json
    nome = new_user.get('nome')
    idade = new_user.get('idade')
    cursor.execute("UPDATE usuarios SET nome = %s, idade = %s WHERE id = %s", (nome, idade, id))
    db.commit()
    logging.info('User updated with success')
    return jsonify({'mensagem': 'User updated with sucess'}), 200

@app.route('/users/', methods=['GET'])
@metrics.do_not_track()
@metrics.counter('read_all_users', 'Number of read all users')
def read_all():
    db = connection_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios")
    users = cursor.fetchall()
    users_list = []
    for user in users:
        user_data = {
            'id': user[0],
            'nome': user[1],
            'idade': user[2]  
        }
        users_list.append(user_data)
    logging.info('Reading all users')
    return jsonify(users_list), 200
if __name__ == '__main__':
    app.run(debug=True)
