FROM python:3.12-slim

WORKDIR /app

# No compiler in the image: every pinned dependency ships manylinux wheels
# for Python 3.12 (the previous build-essential/libpq-dev layer was ~200 MB
# of tools never used at runtime — and never cleaned).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The app may need to create a local SQLite file when no DATABASE_URL is set
# (standalone runs); compose/production use PostgreSQL.
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

# PORT-aware healthcheck (Railway injects PORT).
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,urllib.request,sys; p=os.environ.get('PORT','8000'); sys.exit(0 if urllib.request.urlopen(f'http://127.0.0.1:{p}/api/v1/health', timeout=4).status==200 else 1)"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
