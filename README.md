# GTA: Vice City — WebAssembly (browser port)

This repository ships a **pre-built web client** in `dist/` and a lightweight backend (optional) to:

- serve the static client locally
- proxy game assets (`/vcsky/*`, `/vcbr/*`) from the DOS Zone CDNs
- provide save backends (local disk on Python server, Vercel Blob on Vercel)
- provide a simple WebRTC “signaling” API for the P2P multiplayer UI (Vercel KV / Redis)

> Disclaimer: this is a community-built port and is **not affiliated with Rockstar Games**. Make sure you own the original game if required in your jurisdiction.

## Quick start (local, Python)

Requirements: Python 3.11+ recommended.

```bash
pip install -r requirements.txt
python server.py --port 8000
```

Open `http://localhost:8000`.

### What happens locally?

- `dist/` is served as static files (SPA).
- `/vcsky/*` and `/vcbr/*` are proxied from the DOS Zone CDNs by default.
- **Local saves are enabled by default** on the Python server and stored on disk in `saves/`.

To disable the local save backend:

```bash
python server.py --no_custom_saves
```

## Run with Docker (local)

```bash
docker compose up -d --build
```

Useful environment variables (see `docker-compose.yml`):

| Variable | Purpose |
|---|---|
| `OUT_HOST` / `OUT_PORT` | Exposed bind/port (defaults: `0.0.0.0:8000`) |
| `IN_PORT` | Port inside the container (default: `8000`) |
| `AUTH_LOGIN` / `AUTH_PASSWORD` | Enable HTTP Basic Auth (both required) |
| `VCSKY_CACHE` / `VCBR_CACHE` | Cache proxied files locally (`1` to enable) |
| `VCSKY_LOCAL` / `VCBR_LOCAL` | Serve assets from local folders (`1` to enable) |
| `VCSKY_URL` / `VCBR_URL` | Override upstream CDNs |

Example (cache + auth):

```bash
AUTH_LOGIN=admin AUTH_PASSWORD=secret VCSKY_CACHE=1 VCBR_CACHE=1 docker compose up -d --build
```

## Deploy on Vercel

This repo is ready for Vercel: static files are served from `dist/` and Python serverless functions provide:

- `/vcsky/*` → `api/vcsky.py` (proxy `https://cdn.dos.zone/vcsky/`)
- `/vcbr/*` → `api/vcbr.py` (proxy `https://br.cdn.dos.zone/vcsky/`, with `Content-Encoding: br`)
- `/api/rtc/*` → `api/rtc.py` (WebRTC signaling, requires KV/Redis)
- `/token/*` and `/saves/*` → `api/saves.py` (save storage on Vercel Blob)

### Required Vercel settings

No environment variables are required for the basic game + CDN proxy, but these features are optional:

- **WebRTC signaling** (recommended for multiplayer UI):
  - Connect **Vercel KV** or provide Redis via env
  - Supported env vars:
    - `KV_REST_API_URL`, `KV_REST_API_TOKEN` (Vercel KV / Upstash REST)
    - or `REDIS_URL` / `KV_URL` (TCP Redis URL, `rediss://...` supported)
    - optional: `REDIS_TLS=1` to force TLS
  - optional: `RTC_ROOM_TTL_SECONDS` (default `900`)

- **Persistent saves on Vercel**:
  - Connect **Vercel Blob**
  - Set `BLOB_READ_WRITE_TOKEN` (optional: `BLOB_READ_ONLY_TOKEN`)
  - Then open the game with `?custom_saves=1` to use the “local backend” save SDK against Blob endpoints.

> Note: Vercel serverless functions have execution time limits. Very large upstream downloads may hit timeouts depending on plan and region.

## Server configuration (Python)

The local server is `server.py` (FastAPI + static hosting).

| Flag | Description |
|---|---|
| `--port <int>` | HTTP port (default `8000`) |
| `--login <user>` + `--password <pass>` | Enable HTTP Basic Auth |
| `--vcsky_local` / `--vcbr_local` | Serve from local `vcsky/` / `vcbr/` folders |
| `--vcsky_url` / `--vcbr_url` | Override upstream CDNs |
| `--vcsky_cache` / `--vcbr_cache` | Cache proxied files into `vcsky/` / `vcbr/` |
| `--no_custom_saves` | Disable local save backend |

## URL query parameters (client)

| Param | Values | Meaning |
|---|---|---|
| `lang` | `en` / `ru` | Language |
| `cheats` | `1` | Enable cheat menu (F3) |
| `request_original_game` | `1` | Ask user to provide original files (UI) |
| `fullscreen` | `0` | Disable auto fullscreen |
| `custom_saves` | `1` | Use “local backend” save SDK (mainly for Vercel Blob setup) |

Examples:

- `http://localhost:8000/?lang=ru`
- `http://localhost:8000/?lang=en&cheats=1`

## Project layout (high level)

```
dist/                # pre-built web client (served as-is)
server.py            # local FastAPI server (static + proxies + local saves)
api/                 # Vercel serverless functions (proxies, rtc, saves)
additions/           # auth/cache/saves for local server
docker/              # Docker image (Python runtime)
docker-compose.yml   # local container setup
```

## Credits

- HTML5 port by DOS Zone contributors (see in-game credits / `dist/index.html`)
- Deobfuscation work and repository maintenance by community contributors

## License

MIT (see repository license metadata). Not affiliated with Rockstar Games.
