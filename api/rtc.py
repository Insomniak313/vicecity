import base64
import json
import os
import secrets
from http.server import BaseHTTPRequestHandler
from urllib import request as urllib_request
from urllib.parse import parse_qs, urlparse


def _b64url_encode(text: str) -> str:
    raw = text.encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(text: str) -> str:
    padded = text + "=" * (-len(text) % 4)
    raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    return raw.decode("utf-8")


def _json_response(handler: BaseHTTPRequestHandler, *, status: int, data: dict) -> None:
    payload = json.dumps(data).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(payload)


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("content-length") or "0")
    raw = handler.rfile.read(length) if length > 0 else b"{}"
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return {}


class _UpstashKV:
    """
    Minimal Upstash REST client compatible with Vercel KV env vars:
      - KV_REST_API_URL
      - KV_REST_API_TOKEN

    Note:
      This codebase can also be wired to Upstash directly, but the recommended
      setup for this project is Vercel KV (Vercel Redis/KV integration).

    Uses REST endpoints like:
      GET  {url}/get/{key}
      POST {url}/set/{key}/{value}
      POST {url}/expire/{key}/{seconds}
    """

    def __init__(self) -> None:
        # Vercel KV (official):
        #   KV_REST_API_URL / KV_REST_API_TOKEN (Upstash REST underneath)
        #
        # Upstash direct (also common):
        #   UPSTASH_REDIS_REST_URL / UPSTASH_REDIS_REST_TOKEN
        self.url = (
            os.environ.get("UPSTASH_REDIS_REST_URL")
            or os.environ.get("KV_REST_API_URL")
            or ""
        )
        self.token = (
            os.environ.get("UPSTASH_REDIS_REST_TOKEN")
            or os.environ.get("KV_REST_API_TOKEN")
            # fallback for read-only flows (still useful for GET endpoints)
            or os.environ.get("KV_REST_API_READ_ONLY_TOKEN")
            or ""
        )

    def is_configured(self) -> bool:
        return bool(self.url and self.token)

    def _req(self, method: str, path: str) -> dict:
        url = self.url.rstrip("/") + path
        req = urllib_request.Request(url, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Content-Type", "application/json")
        with urllib_request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return json.loads(raw)
            except Exception:
                return {"raw": raw}

    def get(self, key: str) -> str | None:
        data = self._req("GET", f"/get/{key}")
        if "result" in data:
            raw = data["result"]
            if raw is None:
                return None
            # values are stored as base64url strings (no padding)
            try:
                return _b64url_decode(str(raw))
            except Exception:
                return str(raw)
        return None

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        # Value must be URL-safe in the REST path: store as base64url.
        encoded = _b64url_encode(value)
        self._req("POST", f"/set/{key}/{encoded}")
        self._req("POST", f"/expire/{key}/{ttl_seconds}")


KV = _UpstashKV()
ROOM_TTL_SECONDS = int(os.environ.get("RTC_ROOM_TTL_SECONDS") or "900")  # 15 min


def _room_key(room_id: str, name: str) -> str:
    return f"rtc:{room_id}:{name}"


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if not KV.is_configured():
            return _json_response(
                self,
                status=501,
                data={
                    "error": "Vercel KV not configured",
                    "hint": "Connect Vercel KV (Redis) to this project so KV_REST_API_URL and KV_REST_API_TOKEN are set.",
                },
            )

        path = urlparse(self.path).path
        body = _read_json(self)

        if path.endswith("/rtc/create"):
            room_id = secrets.token_urlsafe(8)
            host_key = secrets.token_urlsafe(16)
            join_key = secrets.token_urlsafe(16)
            # store secrets
            KV.set(_room_key(room_id, "hostKey"), host_key, ROOM_TTL_SECONDS)
            KV.set(_room_key(room_id, "joinKey"), join_key, ROOM_TTL_SECONDS)
            return _json_response(
                self,
                status=200,
                data={"roomId": room_id, "hostKey": host_key, "joinKey": join_key, "ttlSeconds": ROOM_TTL_SECONDS},
            )

        if path.endswith("/rtc/offer"):
            rid = str(body.get("roomId") or "")
            host_key = str(body.get("hostKey") or "")
            offer = str(body.get("offer") or "")
            if not rid or not host_key or not offer:
                return _json_response(self, status=400, data={"error": "missing fields"})
            stored_host_key = KV.get(_room_key(rid, "hostKey"))
            if stored_host_key != host_key:
                return _json_response(self, status=403, data={"error": "invalid hostKey"})
            KV.set(_room_key(rid, "offer"), offer, ROOM_TTL_SECONDS)
            return _json_response(self, status=200, data={"ok": True})

        if path.endswith("/rtc/answer"):
            rid = str(body.get("roomId") or "")
            join_key = str(body.get("joinKey") or "")
            answer = str(body.get("answer") or "")
            if not rid or not join_key or not answer:
                return _json_response(self, status=400, data={"error": "missing fields"})
            stored_join_key = KV.get(_room_key(rid, "joinKey"))
            if stored_join_key != join_key:
                return _json_response(self, status=403, data={"error": "invalid joinKey"})
            KV.set(_room_key(rid, "answer"), answer, ROOM_TTL_SECONDS)
            return _json_response(self, status=200, data={"ok": True})

        return _json_response(self, status=404, data={"error": "not found"})

    def do_GET(self):
        if not KV.is_configured():
            return _json_response(
                self,
                status=501,
                data={
                    "error": "Vercel KV not configured",
                    "hint": "Connect Vercel KV (Redis) to this project so KV_REST_API_URL and KV_REST_API_TOKEN are set.",
                },
            )

        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query or "")
        rid = (qs.get("roomId") or [""])[0]
        if not rid:
            return _json_response(self, status=400, data={"error": "roomId is required"})

        if path.endswith("/rtc/offer"):
            offer = KV.get(_room_key(rid, "offer"))
            return _json_response(self, status=200, data={"offer": offer})

        if path.endswith("/rtc/answer"):
            answer = KV.get(_room_key(rid, "answer"))
            return _json_response(self, status=200, data={"answer": answer})

        return _json_response(self, status=404, data={"error": "not found"})

