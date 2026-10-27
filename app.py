"""
TradingPoint Universal Web Application & API Entrypoint for Vercel.
Handles both static HTML pages and /api serverless endpoints under Python WSGI.
"""

import os
import sys
from urllib.parse import parse_qs

# Import serverless microservice logic
from api.index import app as api_app, handler as api_handler

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon"
}


def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")

    # 1. API Endpoints
    if path.startswith("/api/"):
        return api_app(environ, start_response)

    # 2. Static Pages Mapping
    if path in ["/", "/index.html"]:
        target_file = "index.html"
    elif path in ["/deep_analysis_gold.html", "/deep-analysis-gold"]:
        target_file = "deep_analysis_gold.html"
    elif path in ["/profile.html", "/profile"]:
        target_file = "profile.html"
    elif path in ["/trading_conditions.html", "/trading-conditions"]:
        target_file = "trading_conditions.html"
    else:
        target_file = path.lstrip("/")

    file_path = os.path.join(ROOT_DIR, target_file)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        content_type = MIME_TYPES.get(ext, "application/octet-stream")
        headers = [
            ("Content-Type", content_type),
            ("Cache-Control", "public, max-age=3600")
        ]
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            start_response("200 OK", headers)
            return [content]
        except Exception as e:
            start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
            return [f"Error reading file: {e}".encode("utf-8")]

    # 3. Default Fallback to index.html
    fallback = os.path.join(ROOT_DIR, "index.html")
    if os.path.exists(fallback):
        headers = [("Content-Type", "text/html; charset=utf-8")]
        with open(fallback, "rb") as f:
            content = f.read()
        start_response("200 OK", headers)
        return [content]

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not Found"]


# Expose handler for BaseHTTPRequestHandler runtimes
handler = api_handler
