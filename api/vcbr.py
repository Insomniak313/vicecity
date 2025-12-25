from http.server import BaseHTTPRequestHandler
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Extraire le chemin
            path = self.path
            
            # Enlever le préfixe /vcbr/ si présent
            if '/vcbr/' in path:
                path = path.split('/vcbr/', 1)[1]
            else:
                path = path.lstrip('/')
            
            # Construire l'URL cible
            target_url = f"https://br.cdn.dos.zone/vcsky/{path}"
            
            # Créer la requête
            req = urllib_request.Request(target_url)
            
            # Forward headers importants
            for header in ['User-Agent', 'Accept', 'Accept-Encoding', 'Range']:
                if self.headers.get(header):
                    req.add_header(header, self.headers.get(header))
            
            # Faire la requête
            try:
                with urllib_request.urlopen(req, timeout=10) as response:
                    # Envoyer le status code
                    self.send_response(response.status)
                    
                    # Envoyer les headers CORS
                    self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
                    self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    
                    # Forward les headers importants
                    for header in ['Content-Type', 'Content-Encoding', 'Content-Length', 'Accept-Ranges', 'Content-Range']:
                        value = response.headers.get(header)
                        if value:
                            self.send_header(header, value)
                    
                    self.end_headers()
                    
                    # Envoyer le body
                    self.wfile.write(response.read())
            
            except HTTPError as e:
                self.send_error(e.code, e.reason)
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_msg = json.dumps({'error': str(e)})
            self.wfile.write(error_msg.encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Range')
        self.end_headers()
    
    def do_HEAD(self):
        self.do_GET()
