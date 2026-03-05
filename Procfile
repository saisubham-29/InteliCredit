web: gunicorn -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120
