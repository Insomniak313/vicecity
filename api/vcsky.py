from http.server import BaseHTTPRequestHandler
from urllib import request as urllib_request
from urllib.error import HTTPError
import json
from typing import Optional

class handler(BaseHTTPRequestHandler):
    def _send_proxy(
        self,
        *,
        target_base: str,
        path_prefix: str,
        force_brotli_for_br: bool,
    ) -> None:
        try:
            raw_path = self.path or "/"
            path_only = raw_path.split("?", 1)[0]

            if path_prefix in path_only:
                file_path = path_only.split(path_prefix, 1)[1]
            else:
                file_path = path_only.lstrip("/")

            is_br = file_path.endswith(".br")
            target_url = f"{target_base}{file_path}"

            req = urllib_request.Request(target_url)

            # Forward headers importants (Range essentiel pour les gros fichiers).
            for header in ["User-Agent", "Accept", "Range"]:
                value = self.headers.get(header)
                if value:
                    req.add_header(header, value)

            # Éviter une double compression côté upstream (important si on récupère déjà un fichier *.br).
            if is_br:
                req.add_header("Accept-Encoding", "identity")
            else:
                ae = self.headers.get("Accept-Encoding")
                if ae:
                    req.add_header("Accept-Encoding", ae)

            try:
                with urllib_request.urlopen(req, timeout=60) as response:
                    self.send_response(response.status)

                    # Headers COOP/COEP nécessaires au fonctionnement WASM (SharedArrayBuffer, etc.).
                    self.send_header("Cross-Origin-Opener-Policy", "same-origin")
                    self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
                    self.send_header("Access-Control-Allow-Origin", "*")

                    content_type: Optional[str] = response.headers.get("Content-Type")
                    if is_br and file_path.endswith(".wasm.br"):
                        content_type = "application/wasm"
                    if content_type:
                        self.send_header("Content-Type", content_type)

                    content_encoding = response.headers.get("Content-Encoding")
                    if force_brotli_for_br and is_br:
                        content_encoding = "br"
                    if content_encoding:
                        self.send_header("Content-Encoding", content_encoding)

                    for header in ["Content-Length", "Accept-Ranges", "Content-Range", "Cache-Control", "ETag", "Last-Modified"]:
                        value = response.headers.get(header)
                        if value:
                            self.send_header(header, value)

                    self.end_headers()

                    if self.command == "HEAD":
                        return

                    # Stream (ne pas charger tout le fichier en mémoire: crucial pour .data/.wasm).
                    while True:
                        chunk = response.read(64 * 1024)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
            
            except HTTPError as e:
                self.send_error(e.code, e.reason)
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_msg = json.dumps({'error': str(e)})
            self.wfile.write(error_msg.encode())

    def do_GET(self):
        self._send_proxy(
            target_base="https://cdn.dos.zone/vcsky/",
            path_prefix="/vcsky/",
            force_brotli_for_br=False,
        )
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Range')
        self.end_headers()
    
    def do_HEAD(self):
        self._send_proxy(
            target_base="https://cdn.dos.zone/vcsky/",
            path_prefix="/vcsky/",
            force_brotli_for_br=False,
        )
