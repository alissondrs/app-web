from flask import Flask, jsonify, request
import json
from flask_cors import CORS
from mysql_scripts.db_mysql import connection_db
import logging
# from pythonjsonlogger import jsonlogger
from prometheus_flask_exporter import PrometheusMetrics, Gauge, Counter, Summary, Histogram

# Configurar o logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
app = Flask(__name__)
CORS(app)
metrics = PrometheusMetrics(app, group_by='endpoint')
metrics.info('app_info', 'App Information', version='1.0.3')
labels={
    'status': lambda r: r.status_code if r is not None else 'no_response',
    'route': lambda: request.path if request else 'no_request',
    'endpoint': lambda: request.endpoint if request else 'no_request',
    'method': lambda: request.method if request else 'no_request',
}

# jls_extract_var = metrics
# metrics.register_default(
#     metrics.counter('app_request_total', 'Total HTTP requests', labels=labels),
#     metrics.gauge('app_request_duration_seconds', 'HTTP request duration in seconds', labels=labels ),
#     metrics.summary('app_request_duration_seconds_summary', 'HTTP request duration in seconds summary', labels=labels),
#     metrics.histogram('app_request_duration_seconds_histogram', 'HTTP request duration in seconds histogram', labels=labels)
# )

@app.route('/health', methods=['GET'], endpoint='health')
# 
@metrics.counter('app_health_check_total', 'Number of health checks', labels=labels)
@metrics.gauge('app_health_check_status', 'Health check status', labels={'status': 'status'})
@metrics.summary('app_health_check_summary', 'Health check summary', labels=labels)
@metrics.histogram('app_health_check_histogram', 'Health check histogram', labels=labels)

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
@app.route('/user/<int:id>', methods=['GET'], endpoint='read')
# 
@metrics.counter('app_read_user', 'Number of read users', labels=labels)
@metrics.gauge('app_read_user_status', 'Read user status', labels=labels)	
@metrics.summary('app_read_user_summary', 'Read user summary', labels=labels)
@metrics.histogram('app_read_user_histogram', 'Read user histogram', labels=labels)
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
     
@app.route('/user/', methods=['POST'], endpoint='create')
# 
@metrics.counter('app_create_user', 'Number of create users', labels=labels)
@metrics.gauge('app_create_user_status', 'Create user status', labels=labels)
@metrics.summary('app_create_user_summary', 'Create user summary', labels=labels)
@metrics.histogram('app_create_user_histogram', 'Create user histogram', labels=labels)
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

@app.route('/user/<int:id>', methods=['DELETE'], endpoint='delete')
# 
@metrics.counter('app_delete_user', 'Number of delete users', labels=labels)
@metrics.gauge('app_delete_user_status', 'Delete user status', labels=labels)
@metrics.summary('app_delete_user_summary', 'Delete user summary', labels=labels)
@metrics.histogram('app_delete_user_histogram', 'Delete user histogram', labels=labels)
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
    return jsonify({'mensagem': 'User deleted with sucess'}), 204

@app.route('/user/<int:id>', methods=['PUT'], endpoint='update')
# 
@metrics.counter('app_update_user', 'Number of update users', labels=labels)
@metrics.gauge('app_update_user_status', 'Update user status', labels=labels)
@metrics.summary('app_update_user_summary', 'Update user summary', labels=labels)
@metrics.histogram('app_update_user_histogram', 'Update user histogram', labels=labels)
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

@app.route('/users/', methods=['GET'], endpoint='read_all')
# 
@metrics.counter('read_all_users', 'Number of read all users', labels=labels)
@metrics.gauge('read_all_users_status', 'Read all users status', labels=labels)
@metrics.summary('read_all_users_summary', 'Read all users summary', labels=labels)
@metrics.histogram('read_all_users_histogram', 'Read all users histogram', labels=labels)
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
