"""Shared-hosting (cPanel / Passenger) entrypoint — exposes a WSGI `application`.

FastAPI is ASGI; cPanel's "Setup Python App" (Passenger) serves WSGI.
a2wsgi bridges the two. Railway/Docker keep launching uvicorn directly —
this file is only imported by shared hosts that expect `wsgi.py`.

Local smoke:  python wsgi.py  → http://127.0.0.1:8000
"""

from __future__ import annotations

from a2wsgi import ASGIMiddleware

from app.main import app as fastapi_app

# Passenger/cPanel loads this module and looks for `application`.
application = ASGIMiddleware(fastapi_app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)
