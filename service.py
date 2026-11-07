"""A small JSON HTTP service for the Docker CI/CD assignment."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        version = os.environ.get("APP_VERSION", "local")
        routes = {
            "/": {"message": "Hello from the Python CI/CD service!", "version": version},
            "/health": {"status": "ok"},
            "/version": {"version": version},
        }
        status = 200 if path in routes else 404
        payload = routes.get(path, {"error": "Not found"})
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Listening on port {port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
