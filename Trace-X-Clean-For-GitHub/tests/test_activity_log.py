import tempfile
import unittest

from backend.config import Config


class ActivityLogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.original_database_uri = Config.SQLALCHEMY_DATABASE_URI
        Config.SQLALCHEMY_DATABASE_URI = f"sqlite:///{cls.temp_dir.name}/activity.db"
        from backend.app import app
        cls.app = app
        cls.app.config["TESTING"] = True

    @classmethod
    def tearDownClass(cls):
        from backend.extensions import db
        with cls.app.app_context():
            db.engine.dispose()
        Config.SQLALCHEMY_DATABASE_URI = cls.original_database_uri
        cls.temp_dir.cleanup()

    def test_auth_activity_is_admin_only_and_paged(self):
        client = self.app.test_client()
        failed_login = client.post("/api/auth/login", json={
            "username": "missing-user",
            "password": "not-a-password"
        })
        self.assertEqual(failed_login.status_code, 401)

        admin_login = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        self.assertEqual(admin_login.status_code, 200)

        activities = client.get("/api/admin/activity?limit=2&offset=0")
        self.assertEqual(activities.status_code, 200)
        payload = activities.get_json()
        self.assertGreaterEqual(payload["total"], 2)
        self.assertEqual(len(payload["activities"]), 2)
        self.assertEqual(payload["activities"][0]["action"], "login")
        self.assertEqual(payload["activities"][1]["action"], "login_failed")
        self.assertEqual(payload["activities"][1]["username"], "missing-user")

        invalid_limit = client.get("/api/admin/activity?limit=101")
        self.assertEqual(invalid_limit.status_code, 400)

        logout = client.post("/api/auth/logout")
        self.assertEqual(logout.status_code, 200)
        forbidden = client.get("/api/admin/activity")
        self.assertEqual(forbidden.status_code, 401)

        client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        all_activities = client.get("/api/admin/activity?limit=10").get_json()["activities"]
        self.assertIn("logout", [activity["action"] for activity in all_activities])
