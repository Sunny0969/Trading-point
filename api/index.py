import os
import sys
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure parent directory is in sys.path
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

try:
    import web_server
except Exception as e:
    web_server = None
    _import_err = str(e)


class handler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if not web_server:
            return self._send_json({"error": "Engine initialization failed", "details": _import_err}, 500)

        try:
            if path.endswith("/api/gold/live") or path == "/api/gold/live":
                data = web_server.get_cached_live_ticker()
                return self._send_json(data)

            elif path.endswith("/api/gold/candles") or path == "/api/gold/candles":
                tf = query.get("timeframe", ["15m"])[0]
                limit = int(query.get("limit", [500])[0])
                data = web_server.get_cached_candles(tf, limit)
                return self._send_json(data)

            elif path.endswith("/api/calendar/live") or path == "/api/calendar/live":
                data = web_server.get_cached_economic_calendar()
                return self._send_json(data)

            elif path.endswith("/api/macro/geopolitical") or path == "/api/macro/geopolitical":
                data = web_server.get_cached_geopolitical_news()
                return self._send_json(data)

            elif path.endswith("/api/macro/drivers") or path == "/api/macro/drivers":
                data = web_server.get_cached_macro_drivers()
                return self._send_json(data)

            elif path.endswith("/api/twelvedata/quotes") or path == "/api/twelvedata/quotes":
                data = web_server.get_cached_twelvedata_quotes()
                return self._send_json(data)

            elif path.endswith("/api/sugra/analyze") or path == "/api/sugra/analyze":
                topic = query.get("topic", [None])[0]
                data = web_server.get_sugra_sentiment(topic)
                return self._send_json(data)

            else:
                return self._send_json({
                    "status": "ok",
                    "engine": "TradingPoint Serverless Microservice",
                    "endpoints": [
                        "/api/gold/live",
                        "/api/gold/candles",
                        "/api/calendar/live",
                        "/api/twelvedata/quotes",
                        "/api/sugra/analyze"
                    ]
                })

        except Exception as e:
            return self._send_json({"error": str(e)}, 500)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if not web_server:
            return self._send_json({"error": "Engine initialization failed", "details": _import_err}, 500)

        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload = json.loads(post_body.decode("utf-8"))
        except Exception:
            payload = {}

        try:
            if path.endswith("/api/sugra/analyze") or path == "/api/sugra/analyze":
                topic = payload.get("topic")
                data = web_server.get_sugra_sentiment(topic)
                return self._send_json(data)
            else:
                return self._send_json({"error": "Not Found"}, 404)
        except Exception as e:
            return self._send_json({"error": str(e)}, 500)
