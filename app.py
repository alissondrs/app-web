from flask import Flask, jsonify, request
import json
from flask_cors import CORS
from mysql_scripts.db_mysql import connection_db

app = Flask(__name__)
CORS(app)

lista = [
    {"id": 1, "nome": "joao", "idade": 25},
    {"id": 2, "nome": "roberto", "idade": 42},
    {"id": 3, "nome": "juliana", "idade": 19},
    {"id": 4, "nome": "andresa", "idade": 35},
    {"id": 5, "nome": "monique", "idade": 28}
]


#Read route
@app.route('/users/<int:id>', methods=['GET'])
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
        # for pessoa in lista:
    #     if pessoa['id'] == id:
    #         return jsonify(pessoa)
    # return jsonify({'mensagem': 'user not found'}), 404
     
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
    for user_id in lista:
        if user_id['id'] == id:
            print(user_id)
            lista.remove(user_id)
            print(lista)
            return jsonify({'mensagem': 'User deleted with sucess'}), 200
    return jsonify({'mensagem': 'user not found'}), 404

@app.route('/user/<int:id>', methods=['PUT'])
def update(id):
    user = None
    for u in lista:
        if u['id'] == id:
            user=u
            break
    if user is None:
        return jsonify({'erro': 'user not found'}), 404
    # push data from request to user
    dados = request.json
    user['nome'] = dados.get('nome', user['nome'])
    user['idade'] = dados.get('idade', user['idade'])
    print(lista)

    return jsonify(user), 200

if __name__ == '__main__':
    app.run(debug=True)
