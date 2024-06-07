import unittest
import json
from app import app
from mysql_scripts.db_mysql import connection_db

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.db = connection_db()

    def test_health(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'mensagem': 'Health check ok'})

    def test_read(self):
        # Substitua 1 pelo ID do usuário que você sabe que existe no banco de dados
        response = self.app.get('/user/1')
        self.assertEqual(response.status_code, 200)
        # Verifique se a resposta contém os campos esperados
        json_data = response.get_json()
        self.assertIn('id', json_data)
        self.assertIn('nome', json_data)
        self.assertIn('idade', json_data)

    def test_create(self):
        # Substitua 'nome' e 'idade' pelos valores que você deseja testar
        response = self.app.post('/user/', json={'nome': 'nome', 'idade': 'idade'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {'mensagem': 'user created with susses'})

    def test_delete(self):
        # Substitua 1 pelo ID do usuário que você deseja testar a exclusão
        response = self.app.delete('/user/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'mensagem': 'User deleted with sucess'})

    def test_update(self):
        # Substitua 1 pelo ID do usuário que você deseja testar a atualização
        response = self.app.put('/user/1', json={'nome': 'novo nome', 'idade': 'nova idade'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'mensagem': 'User updated with sucess'})

    def test_read_all(self):
        response = self.app.get('/users/')
        self.assertEqual(response.status_code, 200)
        # Verifique se a resposta é uma lista
        self.assertIsInstance(response.get_json(), list)

if __name__ == '__main__':
    unittest.main()