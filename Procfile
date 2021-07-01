release: . ./scripts/env/production.sh; flask db upgrade
web: python manage.py compile-translations; bin/start-nginx bash ./scripts/wsgi/production.sh gunicorn
worker: . ./scripts/env/production.sh; python manage.py run-worker
