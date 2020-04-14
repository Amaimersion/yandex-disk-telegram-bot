"""
Configurations of the gunicorn server for specific environments.
"""

import os
import multiprocessing


IS_DEVELOPMENT = (os.getenv("FLASK_ENV", "production") == "development")
SERVER_READY_FILE = "/tmp/gunicorn-ready"

# gunicorn settings
reload = IS_DEVELOPMENT
accesslog = "-"
errorlog = "-"
loglevel = ("debug" if IS_DEVELOPMENT else "info")
syslog = True
sendfile = True
bind = "unix:/tmp/nginx-gunicorn.socket"
keepalive = 15
"""
It is I/O bound app, so, we will use “pseudo-threads” (`gevent`).
`threads` setting is only for `gthread` worker.
`worker_connections` setting is only for either `eventlet` or `gevent` workers.
"""
worker_class = "gevent"
workers = multiprocessing.cpu_count() * 2 + 1
workers = (2 if (IS_DEVELOPMENT and workers > 2) else workers)
workers = int(os.getenv("GUNICORN_WORKERS", workers))
threads = int(os.getenv("GUNICORN_THREADS", 1))
worker_connections = int(os.getenv("GUNICORN_WORKER_CONNECTIONS", 1024))


def when_ready(server):
    with open(SERVER_READY_FILE, 'w'):
        pass


def on_exit(server):
    try:
        os.remove(SERVER_READY_FILE)
    except FileNotFoundError:
        pass
