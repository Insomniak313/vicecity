from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse

VCSKY_BASE_URL = "https://cdn.dos.zone/vcsky/"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract the path after /vcsky/
        path = self.path.replace('/vcsky/', '', 1)
        
        # Build the full URL
        url = urllib.parse.urljoin(VCSKY_BASE_URL, path)
        
        try:
            # Proxy the request
            req = urllib.request.Request(url)
            
            # Forward some headers
            for header in ['User-Agent', 'Accept', 'Accept-Encoding']:
                if header in self.headers:
                    req.add_header(header, self.headers[header])
            
            with urllib.request.urlopen(req) as response:
                # Set response headers
                self.send_response(response.status)
                
                # Add CORS headers
                self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
                self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
                self.send_header('Access-Control-Allow-Origin', '*')
                
                # Forward content-type and other headers
                for header, value in response.headers.items():
                    if header.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                        self.send_header(header, value)
                
                self.end_headers()
                
                # Stream the response
                self.wfile.write(response.read())
                
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
    
    def do_POST(self):
        self.do_GET()
    
    def do_PUT(self):
        self.do_GET()
    
    def do_DELETE(self):
        self.do_GET()
    
    def do_PATCH(self):
        self.do_GET()
    
    def do_HEAD(self):
        self.do_GET()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
