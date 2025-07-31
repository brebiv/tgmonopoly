#!/usr/bin/env bash
set -e

# Wait a little in case DB just became "healthy"
sleep 2

# DB migrations (safe to run every start)
# uv run manage.py migrate --noinput

# Collect static (includes Vite build you've copied in)
uv run manage.py collectstatic --noinput

# Run app server
uv run daphne -b 0.0.0.0 -p 8000 tgmonopoly.asgi:application
# gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
