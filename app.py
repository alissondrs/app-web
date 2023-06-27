from flask import Flask, jsonify, request
import json
from flask_cors import CORS

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
# Iterar sobre a lista de users e imprimir o ID de cada um
    for pessoa in lista:
        if pessoa['id'] == id:
            return jsonify(pessoa)
    return jsonify({'mensagem': 'user not found'}), 404
     
@app.route('/users/', methods=['POST'])
def create():
    new_user = request.json
    last_id = max(user_id["id"] for user_id in lista)    
    id = last_id +1
    nome = new_user.get('nome')
    idade = new_user.get('idade')
    
    # verify if user already exists
    for user in lista:
        if user['id'] == id:
            return jsonify({'mensagem': 'user already exists'}), 409
    
    # add user to list
    user = {'id': id, 'nome': nome, 'idade': idade}
    lista.append(user)
    print(lista)
    
    #return success message
    return jsonify({'mensagem': 'user created with susses'}), 201 

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
