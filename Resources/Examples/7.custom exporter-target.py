import http.server
import json

APP_PORT = 8000

webapp_visitors_data={
  "visitors_served": 2831,
  "traffic_channel": {
    "organic": 1210,
    "direct": 601,
    "returning": 1020
  }
}

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(json.dumps(webapp_visitors_data), "UTF-8"))

if __name__ == "__main__":
    server = http.server.HTTPServer(('localhost', APP_PORT), Handler)
    server.serve_forever()
