"""Fictional delivery API with basic Prometheus-compatible metrics."""

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


DELIVERIES = {
    "DEL-1001": {
        "id": "DEL-1001",
        "status": "out_for_delivery",
        "destination": "London",
    },
    "DEL-1002": {
        "id": "DEL-1002",
        "status": "delivered",
        "destination": "Manchester",
    },
}

METRICS_LOCK = threading.Lock()
REQUEST_COUNTS = {}
REQUEST_DURATION_COUNT = 0
REQUEST_DURATION_SUM = 0.0


def record_request(route, status, duration):
    """Record a completed application request."""
    global REQUEST_DURATION_COUNT, REQUEST_DURATION_SUM

    with METRICS_LOCK:
        key = (route, str(status))
        REQUEST_COUNTS[key] = REQUEST_COUNTS.get(key, 0) + 1
        REQUEST_DURATION_COUNT += 1
        REQUEST_DURATION_SUM += duration


def render_metrics():
    """Return metrics in Prometheus text exposition format."""
    with METRICS_LOCK:
        counts = dict(REQUEST_COUNTS)
        duration_count = REQUEST_DURATION_COUNT
        duration_sum = REQUEST_DURATION_SUM

    lines = [
        "# HELP delivery_api_requests_total Total API requests.",
        "# TYPE delivery_api_requests_total counter",
    ]

    for (route, status), count in sorted(counts.items()):
        lines.append(
            f'delivery_api_requests_total{{route="{route}",'
            f'status="{status}"}} {count}'
        )

    lines.extend(
        [
            "# HELP delivery_api_request_duration_seconds "
            "Time spent handling API requests.",
            "# TYPE delivery_api_request_duration_seconds summary",
            f"delivery_api_request_duration_seconds_count {duration_count}",
            f"delivery_api_request_duration_seconds_sum {duration_sum:.6f}",
        ]
    )

    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        start = time.perf_counter()
        path = urlsplit(self.path).path

        if path == "/metrics":
            payload = render_metrics().encode("utf-8")
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/plain; version=0.0.4; charset=utf-8",
            )
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if path == "/healthz":
            route = "/healthz"
            status, body = 200, {"status": "ok"}

        elif path == "/readyz":
            route = "/readyz"
            status, body = 200, {"status": "ready"}

        elif path == "/deliveries":
            route = "/deliveries"
            status, body = 200, {
                "deliveries": list(DELIVERIES.values())
            }

        elif path.startswith("/deliveries/") and path.count("/") == 2:
            route = "/deliveries/{id}"
            delivery_id = path.removeprefix("/deliveries/")
            delivery = DELIVERIES.get(delivery_id)

            if delivery:
                status, body = 200, delivery
            else:
                status, body = 404, {"error": "delivery not found"}

        else:
            route = "other"
            status, body = 404, {"error": "not found"}

        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

        record_request(route, status, time.perf_counter() - start)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()