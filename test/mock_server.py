import http.server
import json
import logging
logger = logging.getLogger(__name__)

class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/v1/chat/completions":
            self.send_error(405)
            return
        self.send_error(404)

    def do_POST(self):
        # content type must be "application/json"
        print("post")
        if not self.headers.get_content_type().startswith("application/json"):
            self.send_error(400)
            return

        if self.path == "/v1/chat/completions":
            self.do_completions()
            return
        self.send_error(404)

    def do_completions(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            self.send_error(400)
            return
        try:
            body = json.loads(self.rfile.read(length))
        except json.decoder.JSONDecodeError:
            self.send_error(400)
            return

        msgs = body.get("messages", [])
        if len(msgs) == 0:
            self.send_error(400)
            return

        content = msgs[-1].get("content", "")
        resp = {
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "reasoning_content": content,
                    "content": f"result:\n```\n{content}\n```"
                    },
                }],
            }
        resp_json = json.dumps(resp)
        resp_body = resp_json.encode("utf8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(resp_body)))
        self.end_headers()
        self.wfile.write(resp_body)

def start_server(host="", port=8080):
    server_address = (host, port)
    httpd = http.server.HTTPServer(server_address, HTTPRequestHandler)
    logger.info(f"start HTTP server on {host}:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    start_server()
