import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.models import db
from app.models.history import QueryLog
from app.services.cache import cache_service

class BlackHoleTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("development")
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
        cache_service.clear()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        cache_service.clear()

    def test_homepage_render(self):
        """Test homepage renders with HTTP 200 and BlackHole branding."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Black", response.data)
        self.assertIn(b"Hole", response.data)
        self.assertIn(b"Search the universe", response.data)

    def test_api_ai_summary_endpoint(self):
        """Test /api/ai-summary endpoint returns structured AI synthesis."""
        response = self.client.get("/api/ai-summary?q=neural+networks&model=deepseek-r1")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["query"], "neural networks")
        self.assertIn("BlackHole AI", data["model_name"])
        self.assertIn("summary", data)

    def test_search_valid_query(self):
        """Test valid search query returns structured JSON."""
        response = self.client.get("/search?q=gravitational+lens")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["query"], "gravitational lens")
        self.assertIsInstance(data["items"], list)
        self.assertGreater(len(data["items"]), 0)
        self.assertIn("title", data["items"][0])
        self.assertIn("snippet", data["items"][0])
        self.assertIn("link", data["items"][0])

    def test_search_empty_query(self):
        """Test empty search query returns HTTP 400 error."""
        response = self.client.get("/search?q=")
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["items"], [])

    def test_caching_layer(self):
        """Test caching: 1st call cached=False, 2nd call cached=True."""
        r1 = self.client.get("/search?q=supernova").get_json()
        self.assertFalse(r1["cached"])

        r2 = self.client.get("/search?q=supernova").get_json()
        self.assertTrue(r2["cached"])

    def test_query_logging_and_trending(self):
        """Test SQLite logging and trending query retrieval."""
        from sqlalchemy import select
        self.client.get("/search?q=quasar")
        self.client.get("/search?q=quasar")
        self.client.get("/search?q=nebula")

        with self.app.app_context():
            logs = db.session.scalars(select(QueryLog)).all()
            self.assertEqual(len(logs), 3)

            trending = QueryLog.get_trending(limit=5)
            self.assertGreaterEqual(len(trending), 2)
            self.assertEqual(trending[0]["query"].lower(), "quasar")
            self.assertEqual(trending[0]["count"], 2)

    def test_api_trending_endpoint(self):
        """Test /api/trending JSON endpoint."""
        self.client.get("/search?q=event+horizon")
        response = self.client.get("/api/trending")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIsInstance(data["trending"], list)

if __name__ == "__main__":
    unittest.main()
