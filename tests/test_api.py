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
        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True,
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()
        cls.server.server_close()

    def request(self, path):
        conn = HTTPConnection(
            "127.0.0.1",
            self.server.server_port,
            timeout=3,
        )

        try:
            conn.request("GET", path)
            response = conn.getresponse()
            body = response.read().decode("utf-8")
            return response.status, response.getheader("Content-Type"), body
        finally:
            conn.close()

    def test_health_and_readiness(self):
        for path in ("/healthz", "/readyz"):
            with self.subTest(path=path):
                status, _, _ = self.request(path)
                self.assertEqual(status, 200)

    def test_list_and_get(self):
        status, _, body = self.request("/deliveries")
        self.assertEqual(status, 200)
        self.assertEqual(len(json.loads(body)["deliveries"]), 2)

        status, _, body = self.request("/deliveries/DEL-1001")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["status"], "out_for_delivery")

    def test_missing_delivery_and_route(self):
        for path in ("/deliveries/unknown", "/unknown"):
            with self.subTest(path=path):
                status, _, _ = self.request(path)
                self.assertEqual(status, 404)

    def test_metrics_record_requests(self):
        self.request("/deliveries/DEL-1001")
        self.request("/deliveries/unknown")

        status, content_type, body = self.request("/metrics")

        self.assertEqual(status, 200)
        self.assertTrue(content_type.startswith("text/plain"))
        self.assertIn(
            'delivery_api_requests_total{route="/deliveries/{id}",'
            'status="200"}',
            body,
        )
        self.assertIn(
            'delivery_api_requests_total{route="/deliveries/{id}",'
            'status="404"}',
            body,
        )
        self.assertIn("delivery_api_request_duration_seconds_count", body)
        self.assertIn("delivery_api_request_duration_seconds_sum", body)


if __name__ == "__main__":
    unittest.main()