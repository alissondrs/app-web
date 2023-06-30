from flask import Flask, jsonify, request
import json
from flask_cors import CORS
from mysql_scripts.db_mysql import connection_db

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

#Read route
@app.route('/user/<int:id>', methods=['GET'])
def read(id):
    db = connection_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    user = cursor.fetchone()

    if user:
        user_data = {
            'id': user[0],
            'nome': user[1],
            'idade': user[2]  
        }
        return jsonify(user_data), 200
    else:
        return jsonify({'mensagem': 'user not found'}), 404
     
@app.route('/user/', methods=['POST'])
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
        return jsonify({'mensagem': 'user already exists'}), 409
    #create new user
    cursor.execute("INSERT INTO usuarios (nome, idade) VALUES (%s, %s)", (nome, idade))
    db.commit()
    #verify if new user was created
    if cursor.rowcount == 1:
        return jsonify({'mensagem': 'user created with susses'}), 201
    else:
        return jsonify({'mensagem': 'user not created'}), 400

@app.route('/user/<int:id>', methods=['DELETE'])
def delete(id):
    db = connection_db()
    cursor = db.cursor()
    #verify if user exists
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'mensagem': 'user not found'}), 404
    # delete user
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    db.commit()
    return jsonify({'mensagem': 'User deleted with sucess'}), 200

@app.route('/user/<int:id>', methods=['PUT'])
def update(id):
    db = connection_db()
    cursor = db.cursor()
    #verify if user exists
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'mensagem': 'user not found'}), 404
    #update user
    new_user = request.json
    nome = new_user.get('nome')
    idade = new_user.get('idade')
    cursor.execute("UPDATE usuarios SET nome = %s, idade = %s WHERE id = %s", (nome, idade, id))
    db.commit()
    return jsonify({'mensagem': 'User updated with sucess'}), 200

@app.route('/users/', methods=['GET'])
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
    return jsonify(users_list), 200
if __name__ == '__main__':
    app.run(debug=True)
