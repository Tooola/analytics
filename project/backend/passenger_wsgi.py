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

# Change current working directory to backend root so .env and relative DB paths are found
try:
    os.chdir(APP_DIR)
except Exception:
    pass

try:
    from a2wsgi import ASGIMiddleware
    from app.main import app as fastapi_app

    # Phusion Passenger looks for `application`
    _asgi_app = ASGIMiddleware(fastapi_app)

    def application(environ, start_response):
        try:
            return _asgi_app(environ, start_response)
        except Exception:
            import traceback
            tb = traceback.format_exc()
            start_response("500 Internal Server Error", [("Content-Type", "text/plain; charset=utf-8")])
            return [f"Erreur d'exécution FastAPI/Passenger :\n\n{tb}\n".encode("utf-8")]

except Exception as exc:
    # Diagnostic d'erreur clair si une dépendance manque ou plante au démarrage
    import traceback
    tb = traceback.format_exc()
    
    def application(environ, start_response):
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        msg = f"Erreur de démarrage Backend (Phusion Passenger) :\n\n{tb}\n"
        return [msg.encode("utf-8")]

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)
