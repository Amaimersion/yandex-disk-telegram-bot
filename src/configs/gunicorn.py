"""
Configurations of the gunicorn server for specific environments.
"""

import os
import multiprocessing


is_development = (os.getenv("FLASK_ENV", "production") == "development")

# gunicorn settings
reload = is_development
accesslog = "-"
errorlog = "-"
loglevel = ("debug" if is_development else "info")
syslog = True
bind = "localhost:8000"
# it is I/O bound app
worker_class = "gevent"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 1
worker_connections = 1024
