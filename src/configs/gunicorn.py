"""
Configurations of the gunicorn server for specific environments.
"""

import os
import multiprocessing


IS_DEVELOPMENT = (os.getenv("FLASK_ENV", "production") == "development")
SERVER_READY_FILE = "/tmp/gunicorn-ready"

# gunicorn settings
reload = IS_DEVELOPMENT
accesslog = os.getenv("GUNICORN_ACCESS_LOG_PATH", "-")
errorlog = os.getenv("GUNICORN_ERROR_LOG_PATH", "-")
loglevel = ("debug" if IS_DEVELOPMENT else "info")
syslog = True
sendfile = True
bind = "unix:/tmp/nginx-gunicorn.socket"
keepalive = 15
# it is I/O bound app
worker_class = "gevent"
workers = multiprocessing.cpu_count() * 2 + 1
workers = (4 if workers > 4 else workers)
workers = os.getenv("GUNICORN_WORKERS", workers)
threads = os.getenv("GUNICORN_THREADS", 1)
worker_connections = os.getenv("GUNICORN_WORKER_CONNECTIONS", 1024)


def when_ready(server):
    with open(SERVER_READY_FILE, 'w'):
        pass


def on_exit(server):
    try:
        os.remove(SERVER_READY_FILE)
    except FileNotFoundError:
        pass
