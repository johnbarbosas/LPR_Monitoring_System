from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO

class RequestHandler(BaseHTTPRequestHandler):
    last_message = ""

    def _send_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        message = body.decode('utf-8')
        self.last_message = message

        # Save the last message to a text file
        with open('last_message.txt', 'w') as file:
            file.write(message)

        self._send_response(f"Received POST request with body: {message}")

def run_server(port=8081):
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
