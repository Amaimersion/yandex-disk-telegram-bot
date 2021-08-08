"""
Configurations of gunicorn server for specific environments.
"""

import os
import multiprocessing


# region Env & Constants

FLASK_ENV = os.getenv(
    "FLASK_ENV",
    "production"
)
PORT = os.getenv(
    "GUNICORN_PORT",
    "8080"
)
UNIX_SOCKET_PATH = os.getenv(
    "GUNICORN_UNIX_SOCKET_PATH",
    "/tmp/nginx-gunicorn.socket"
)
USE_IP_SOCKET = bool(os.getenv(
    "GUNICORN_USE_IP_SOCKET",
    False
))
WORKERS = int(os.getenv(
    "GUNICORN_WORKERS",
    -1 # -1 means "auto"
))
THREADS = int(os.getenv(
    "GUNICORN_THREADS",
    1
))
WORKER_CONNECTIONS = int(os.getenv(
    "GUNICORN_WORKER_CONNECTIONS",
    1024
))
ACCESS_LOG = os.getenv(
    "GUNICORN_ACCESS_LOG",
    "-" # means "stdout"
)
ERROR_LOG = os.getenv(
    "GUNICORN_ERROR_LOG",
    "-" # means "stderr"
)

IS_DEVELOPMENT = (FLASK_ENV == "development")
SERVER_READY_FILE = "/tmp/gunicorn-ready"

# endregion


# region gunicorn config

reload = IS_DEVELOPMENT
accesslog = ACCESS_LOG
errorlog = ERROR_LOG
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" '
    '%(s)s %(b)s "%(f)s" "%(a)s" %(L)s seconds'
)
loglevel = (
    "debug"
    if IS_DEVELOPMENT else
    "info"
)
syslog = True
sendfile = True
bind = (
    f"0.0.0.0:{PORT}"
    if USE_IP_SOCKET else
    f"unix:{UNIX_SOCKET_PATH}"
)
keepalive = 15
"""
It is I/O bound app, so, we will use “pseudo-threads” (`gevent`).
`threads` setting is only for `gthread` worker.
`worker_connections` setting is only for either `eventlet` or `gevent` workers.
"""
worker_class = "gevent"
workers = (multiprocessing.cpu_count() * 2 + 1)
workers = (
    2
    if (IS_DEVELOPMENT and workers > 2) else
    workers
)
workers = (
    WORKERS
    if (WORKERS != -1) else
    workers
)
threads = THREADS
worker_connections = WORKER_CONNECTIONS


def when_ready(server):
    with open(SERVER_READY_FILE, 'w'):
        pass


def on_exit(server):
    try:
        os.remove(SERVER_READY_FILE)
    except FileNotFoundError:
        pass

# endregion
