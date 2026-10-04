"""A stand-in for the imajev server: answers every request with fixed probabilities and its model name."""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT, NAME = int(sys.argv[1]), sys.argv[2]
ANSWERS = {"q1_gradeable": {"type": "noul", "noul": 0.9, "unknown_probability": 0.0},
           "q2_grade": {"type": "score", "probabilities": {"0": 0.6, "1": 0.2, "2": 0.1, "3": 0.05, "4": 0.05}, "unknown_probability": 0.1},
           "q3_maculopathy": {"type": "noul", "noul": 0.2, "unknown_probability": 0.2},
           "q4_refer": {"type": "noul", "noul": 0.3, "unknown_probability": 0.2},
           "q5_sight": {"type": "noul", "noul": 0.15, "unknown_probability": 0.1}}


class H(BaseHTTPRequestHandler):
    def _send(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send({"models": [NAME]})

    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        self._send({"model": NAME, "answers": ANSWERS})

    def log_message(self, *a):
        pass


HTTPServer(("127.0.0.1", PORT), H).serve_forever()
