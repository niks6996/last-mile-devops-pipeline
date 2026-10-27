import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from app.server import Handler

class APITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()
        cls.server.server_close()

    def request(self, path):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            conn.request("GET", path)
            response = conn.getresponse()
            return response.status, json.loads(response.read())
        finally:
            conn.close()

    def test_health_and_readiness(self):
        for path in ("/healthz", "/readyz"):
            with self.subTest(path=path):
                self.assertEqual(self.request(path)[0], 200)

    def test_list_and_get(self):
        self.assertEqual(len(self.request('/deliveries')[1]['deliveries']), 2)
        self.assertEqual(self.request('/deliveries/DEL-1001')[1]['status'], 'out_for_delivery')

    def test_missing_delivery_and_route(self):
        for path in ('/deliveries/unknown', '/unknown'):
            with self.subTest(path=path):
                self.assertEqual(self.request(path)[0], 404)

if __name__ == '__main__':
    unittest.main()
