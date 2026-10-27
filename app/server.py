"""Small, read-only simulated delivery API using the Python standard library."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

DELIVERIES = {
    "DEL-1001": {"id": "DEL-1001", "status": "out_for_delivery", "destination": "London"},
    "DEL-1002": {"id": "DEL-1002", "status": "delivered", "destination": "Manchester"},
}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/healthz":
            status, body = 200, {"status": "ok"}
        elif path == "/readyz":
            status, body = 200, {"status": "ready"}
        elif path == "/deliveries":
            status, body = 200, {"deliveries": list(DELIVERIES.values())}
        elif path.startswith("/deliveries/") and path.count("/") == 2:
            delivery = DELIVERIES.get(path.removeprefix("/deliveries/"))
            status, body = (200, delivery) if delivery else (404, {"error": "delivery not found"})
        else:
            status, body = 404, {"error": "not found"}
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
