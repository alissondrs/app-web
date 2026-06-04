import unittest
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "app"))

from app import app


class AppRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("webapp.routes.connection_db")
    def test_health_returns_ok_when_database_is_available(self, mock_connection_db):
        mock_connection_db.return_value = MagicMock()

        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"mensagem": "Health check ok"})

    @patch("webapp.routes.fetch_user_by_id")
    @patch("webapp.routes.connection_db")
    def test_read_returns_user_payload(self, mock_connection_db, mock_fetch_user_by_id):
        mock_connection_db.return_value = MagicMock()
        mock_fetch_user_by_id.return_value = {"id": 1, "nome": "Alice", "idade": 28}

        response = self.client.get("/user/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"id": 1, "nome": "Alice", "idade": 28})

    @patch("webapp.routes.fetch_user_by_name")
    @patch("webapp.routes.create_user")
    @patch("webapp.routes.connection_db")
    def test_create_returns_created_when_payload_is_valid(
        self,
        mock_connection_db,
        mock_create_user,
        mock_fetch_user_by_name,
    ):
        mock_connection_db.return_value = MagicMock()
        mock_fetch_user_by_name.return_value = None
        mock_create_user.return_value = True

        response = self.client.post("/user/", json={"nome": "Alice", "idade": 28})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"mensagem": "user created with susses"})

    def test_create_rejects_invalid_payload(self):
        response = self.client.post("/user/", json={"nome": "", "idade": "abc"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"mensagem": "invalid user payload"})

    @patch("webapp.routes.fetch_all_users")
    @patch("webapp.routes.connection_db")
    def test_read_all_returns_all_users(self, mock_connection_db, mock_fetch_all_users):
        mock_connection_db.return_value = MagicMock()
        mock_fetch_all_users.return_value = [
            {"id": 1, "nome": "Alice", "idade": 28},
            {"id": 2, "nome": "Bob", "idade": 31},
        ]

        response = self.client.get("/users/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            [
                {"id": 1, "nome": "Alice", "idade": 28},
                {"id": 2, "nome": "Bob", "idade": 31},
            ],
        )


if __name__ == "__main__":
    unittest.main()
