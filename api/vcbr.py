from http.server import BaseHTTPRequestHandler
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Extract the path after /vcbr/
            path = self.path.split('/vcbr/')[-1] if '/vcbr/' in self.path else ''
            
            # Build the target URL
            target_url = f"https://br.cdn.dos.zone/vcsky/{path}"
            
            # Create request
            req = urllib.request.Request(target_url)
            
            # Forward headers
            for header in ['User-Agent', 'Accept', 'Accept-Encoding']:
                if self.headers.get(header):
                    req.add_header(header, self.headers.get(header))
            
            # Make request
            with urllib.request.urlopen(req, timeout=10) as response:
                # Send response
                self.send_response(response.status)
                
                # Send CORS headers
                self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
                self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
                self.send_header('Access-Control-Allow-Origin', '*')
                
                # Forward content headers
                if response.headers.get('Content-Type'):
                    self.send_header('Content-Type', response.headers.get('Content-Type'))
                if response.headers.get('Content-Encoding'):
                    self.send_header('Content-Encoding', response.headers.get('Content-Encoding'))
                
                self.end_headers()
                
                # Send body
                self.wfile.write(response.read())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(str(e).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
