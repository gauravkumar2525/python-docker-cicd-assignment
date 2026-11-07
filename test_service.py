import json
import os
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import urlopen

from service import Handler


class ServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def get(self, path):
        with urlopen(self.base_url + path, timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertIn("application/json", response.headers["Content-Type"])
            return json.load(response)

    def test_home_returns_message(self):
        self.assertEqual(self.get("/")["message"], "Hello from the Python CI/CD service!")

    def test_health(self):
        self.assertEqual(self.get("/health"), {"status": "ok"})

    def test_build_version(self):
        with patch.dict(os.environ, {"APP_VERSION": "build-42"}):
            self.assertEqual(self.get("/version"), {"version": "build-42"})

    def test_query_string_does_not_change_route(self):
        self.assertEqual(self.get("/health?probe=true"), {"status": "ok"})

    def test_unknown_route(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.base_url + "/missing", timeout=5)
        self.assertEqual(caught.exception.code, 404)
        self.assertEqual(json.load(caught.exception), {"error": "Not found"})


if __name__ == "__main__":
    unittest.main()
