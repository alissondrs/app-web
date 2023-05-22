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
@app.route('/read/<int:id>', methods=['GET'])
def read(id):
# Iterar sobre a lista de users e imprimir o ID de cada um
    for pessoa in lista:
        if pessoa['id'] == id:
            return jsonify(pessoa)
    return jsonify({'mensagem': 'user not found'}), 404    




if __name__ == '__main__':
    app.run(debug=True)
