"""cPanel Phusion Passenger entrypoint for FastAPI.

cPanel's "Setup Python App" executes this file via Phusion Passenger (WSGI).
a2wsgi bridges ASGI (FastAPI) to WSGI.
"""

from __future__ import annotations

import os
import sys

# Ensure backend root is in sys.path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

try:
    from a2wsgi import ASGIMiddleware
    from app.main import app as fastapi_app

    # Phusion Passenger looks for `application`
    application = ASGIMiddleware(fastapi_app)
except Exception as exc:
    # Fallback pour éviter que cPanel ne bloque "Run Pip Install"
    # tant que les dépendances (a2wsgi, fastapi...) ne sont pas encore installées.
    def application(environ, start_response):
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        msg = f"Application en cours d'initialisation...\nErreur de chargement des modules : {exc}\n"
        return [msg.encode("utf-8")]

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)
