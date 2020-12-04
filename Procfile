release: . ./scripts/env/production.sh; flask db upgrade
web: bin/start-nginx bash ./scripts/wsgi/production.sh gunicorn
worker: python worker.py
