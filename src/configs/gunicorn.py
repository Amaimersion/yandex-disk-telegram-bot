"""
Configurations of the gunicorn server for specific environments.
"""

import os
import multiprocessing


is_development = (os.getenv("FLASK_ENV", "production") == "development")


reload = is_development
accesslog = "-"
errorlog = "-"
loglevel = ("debug" if is_development else "info")
syslog = True
bind = "127.0.0.1:8000"
# it is I/O bound app
worker_class = "gevent"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 1
worker_connections = 1000
