import base64
import json
import os
import secrets
import ssl
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
            # some setups expose Vercel-prefixed names
            or os.environ.get("VERCEL_KV_REST_API_URL")
            or ""
        )
        self.token = (
            os.environ.get("UPSTASH_REDIS_REST_TOKEN")
            or os.environ.get("KV_REST_API_TOKEN")
            or os.environ.get("VERCEL_KV_REST_API_TOKEN")
            # fallback for read-only flows (still useful for GET endpoints)
            or os.environ.get("KV_REST_API_READ_ONLY_TOKEN")
            or os.environ.get("VERCEL_KV_REST_API_READ_ONLY_TOKEN")
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


class _RedisKV:
    """
    Redis client via TCP, configured by a single URL.

    Env:
      - REDIS_URL     (redis://... or rediss://...)
      - REDIS_TLS=1   (optional; forces TLS even if scheme is redis://)
    """

    def __init__(self) -> None:
        # Depending on which Vercel storage integration is connected, the URL
        # may be exposed under different names.
        self.redis_url = (
            os.environ.get("REDIS_URL")
            or os.environ.get("KV_URL")  # common for Vercel KV (rediss://...)
            or os.environ.get("UPSTASH_REDIS_URL")  # Upstash TCP URL
            or os.environ.get("VERCEL_REDIS_URL")
            or ""
        )
        self._client = None

    def is_configured(self) -> bool:
        return bool(self.redis_url)

    def _get_client(self):
        if self._client is not None:
            return self._client

        try:
            import redis  # type: ignore
        except Exception as e:
            raise RuntimeError("Missing dependency: redis") from e

        force_tls = (os.environ.get("REDIS_TLS") or "").strip() == "1"
        use_tls = force_tls or self.redis_url.startswith("rediss://")

        kwargs = {
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "retry_on_timeout": True,
            "decode_responses": True,
        }
        if use_tls:
            kwargs["ssl"] = True
            kwargs["ssl_cert_reqs"] = ssl.CERT_NONE

        self._client = redis.Redis.from_url(self.redis_url, **kwargs)
        return self._client

    def get(self, key: str) -> str | None:
        try:
            return self._get_client().get(key)
        except Exception:
            return None

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        try:
            self._get_client().set(name=key, value=value, ex=ttl_seconds)
        except Exception:
            return


class _KVFacade:
    def __init__(self) -> None:
        self.redis = _RedisKV()
        self.rest = _UpstashKV()

    def is_configured(self) -> bool:
        return self.redis.is_configured() or self.rest.is_configured()

    def get(self, key: str) -> str | None:
        if self.redis.is_configured():
            return self.redis.get(key)
        return self.rest.get(key)

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        if self.redis.is_configured():
            return self.redis.set(key, value, ttl_seconds)
        return self.rest.set(key, value, ttl_seconds)


KV = _KVFacade()
ROOM_TTL_SECONDS = int(os.environ.get("RTC_ROOM_TTL_SECONDS") or "900")  # 15 min


def _room_key(room_id: str, name: str) -> str:
    return f"rtc:{room_id}:{name}"


class handler(BaseHTTPRequestHandler):
    def _kv_diagnostics(self) -> dict:
        # Never return secret values, only presence booleans.
        def _has(name: str) -> bool:
            return bool((os.environ.get(name) or "").strip())

        return {
            "hasREDIS_URL": _has("REDIS_URL"),
            "hasKV_URL": _has("KV_URL"),
            "hasUPSTASH_REDIS_URL": _has("UPSTASH_REDIS_URL"),
            "hasVERCEL_REDIS_URL": _has("VERCEL_REDIS_URL"),
            "hasKV_REST_API_URL": _has("KV_REST_API_URL"),
            "hasKV_REST_API_TOKEN": _has("KV_REST_API_TOKEN"),
            "hasKV_REST_API_READ_ONLY_TOKEN": _has("KV_REST_API_READ_ONLY_TOKEN"),
            "hasUPSTASH_REDIS_REST_URL": _has("UPSTASH_REDIS_REST_URL"),
            "hasUPSTASH_REDIS_REST_TOKEN": _has("UPSTASH_REDIS_REST_TOKEN"),
            "hasVERCEL_KV_REST_API_URL": _has("VERCEL_KV_REST_API_URL"),
            "hasVERCEL_KV_REST_API_TOKEN": _has("VERCEL_KV_REST_API_TOKEN"),
            "hasVERCEL_KV_REST_API_READ_ONLY_TOKEN": _has("VERCEL_KV_REST_API_READ_ONLY_TOKEN"),
        }

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
                    "hint": (
                        "Connect Vercel KV (recommended) so KV_REST_API_URL and KV_REST_API_TOKEN are set, "
                        "or provide a Redis URL via REDIS_URL / KV_URL / UPSTASH_REDIS_URL."
                    ),
                    "diagnostics": self._kv_diagnostics(),
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
                    "hint": (
                        "Connect Vercel KV (recommended) so KV_REST_API_URL and KV_REST_API_TOKEN are set, "
                        "or provide a Redis URL via REDIS_URL / KV_URL / UPSTASH_REDIS_URL."
                    ),
                    "diagnostics": self._kv_diagnostics(),
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

