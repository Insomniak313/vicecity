import json
import os
import re
import cgi
from http.server import BaseHTTPRequestHandler
from urllib import request as urllib_request
from urllib.error import HTTPError
from urllib.parse import parse_qs, unquote, urlparse


def _json_response(handler: BaseHTTPRequestHandler, *, status: int, data: dict) -> None:
    payload = json.dumps(data).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(payload)


def _blob_read_token() -> str:
    return (
        os.environ.get("BLOB_READ_ONLY_TOKEN")
        or os.environ.get("BLOB_READ_WRITE_TOKEN")
        or ""
    )


def _blob_write_token() -> str:
    return os.environ.get("BLOB_READ_WRITE_TOKEN") or ""


def _is_blob_configured_for_read() -> bool:
    return bool(_blob_read_token())


def _is_blob_configured_for_write() -> bool:
    return bool(_blob_write_token())


def _sanitize_token(token: str) -> str:
    # Token attendu: souvent 5 chars, mais on accepte plus large en restant safe.
    token = (token or "").strip()
    token = re.sub(r"[^a-zA-Z0-9_-]", "", token)
    return token[:64]


def _sanitize_filename(file_name: str) -> str:
    # Évite traversal. `fileName` arrive déjà encodé côté client.
    raw = (file_name or "").strip()
    raw = unquote(raw)
    raw = os.path.basename(raw)
    if not raw:
        return "save.bin"
    return raw[:128]


def _blob_object_path(token: str, file_name: str) -> str:
    # Namespace dédié au projet pour éviter collisions.
    safe_token = _sanitize_token(token) or "anon"
    safe_name = _sanitize_filename(file_name)
    return f"revc-saves/{safe_token}/{safe_name}"


def _blob_url(pathname: str) -> str:
    # API “raw” Vercel Blob (auth via Bearer token).
    return f"https://blob.vercel-storage.com/{pathname.lstrip('/')}"


def _blob_request(method: str, pathname: str, *, token: str, data: bytes | None = None) -> urllib_request.Request:
    req = urllib_request.Request(_blob_url(pathname), data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    # On stocke des bytes compressés (LZ4) -> octet-stream
    req.add_header("Content-Type", "application/octet-stream")
    return req


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Range")
        self.end_headers()

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            qs = parse_qs(parsed.query or "")

            # Support /token/get et /api/token/get
            if path.endswith("/token/get"):
                token_id = (qs.get("id") or [""])[0]
                return _json_response(
                    self,
                    status=200,
                    data={"token": token_id, "premium": True, "email": "blob@user"},
                )

            # Support /saves/download/{token}/{fileName} (+ variante /api/saves/...)
            if "/saves/download/" in path:
                parts = [p for p in path.split("/") if p]
                # ... saves download <token> <fileName...>
                try:
                    i = parts.index("saves")
                    if parts[i + 1] != "download":
                        raise ValueError()
                    save_token = parts[i + 2]
                    file_name = "/".join(parts[i + 3 :])  # au cas où
                except Exception:
                    return _json_response(self, status=400, data={"error": "invalid download path"})

                if not _is_blob_configured_for_read():
                    return _json_response(
                        self,
                        status=501,
                        data={
                            "error": "Vercel Blob not configured",
                            "hint": "Set BLOB_READ_WRITE_TOKEN (or BLOB_READ_ONLY_TOKEN) in Vercel Environment Variables.",
                        },
                    )

                blob_path = _blob_object_path(save_token, file_name)
                req = _blob_request("GET", blob_path, token=_blob_read_token())

                try:
                    with urllib_request.urlopen(req, timeout=30) as resp:
                        self.send_response(resp.status)
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.send_header("Cache-Control", "no-store")
                        self.send_header("Content-Type", "application/octet-stream")
                        self.end_headers()

                        while True:
                            chunk = resp.read(64 * 1024)
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                        return
                except HTTPError as e:
                    if e.code == 404:
                        return _json_response(self, status=404, data={"error": "File not found"})
                    return _json_response(self, status=502, data={"error": "Blob upstream error", "status": e.code})

            return _json_response(self, status=404, data={"error": "not found"})

        except Exception as e:
            return _json_response(self, status=500, data={"error": str(e)})

    def do_POST(self):
        try:
            path = urlparse(self.path).path

            # Support /saves/upload (+ variante /api/saves/...)
            if path.endswith("/saves/upload"):
                if not _is_blob_configured_for_write():
                    return _json_response(
                        self,
                        status=501,
                        data={
                            "error": "Vercel Blob not configured",
                            "hint": "Set BLOB_READ_WRITE_TOKEN in Vercel Environment Variables (Storage → Blob).",
                        },
                    )

                content_type = self.headers.get("content-type") or self.headers.get("Content-Type") or ""
                if "multipart/form-data" not in content_type.lower():
                    return _json_response(self, status=400, data={"error": "expected multipart/form-data"})

                environ = {
                    "REQUEST_METHOD": "POST",
                    "CONTENT_TYPE": content_type,
                    "CONTENT_LENGTH": self.headers.get("content-length") or "0",
                }
                form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ=environ, keep_blank_values=True)

                save_token = str(form.getvalue("token") or "")
                file_name = str(form.getvalue("fileName") or "")
                if not save_token or not file_name or "file" not in form:
                    return _json_response(self, status=400, data={"error": "missing fields"})

                file_item = form["file"]
                raw = file_item.file.read() if getattr(file_item, "file", None) else b""
                if not raw:
                    return _json_response(self, status=400, data={"error": "empty file"})

                blob_path = _blob_object_path(save_token, file_name)
                put_req = _blob_request("PUT", blob_path, token=_blob_write_token(), data=raw)

                try:
                    with urllib_request.urlopen(put_req, timeout=30) as resp:
                        # Some responses are JSON, but we don't strictly need it.
                        _ = resp.read()
                        if resp.status not in (200, 201):
                            return _json_response(self, status=502, data={"error": "blob upload failed", "status": resp.status})
                        return _json_response(self, status=200, data={"success": True})
                except HTTPError as e:
                    return _json_response(self, status=502, data={"error": "blob upload error", "status": e.code})

            return _json_response(self, status=404, data={"error": "not found"})

        except Exception as e:
            return _json_response(self, status=500, data={"error": str(e)})

