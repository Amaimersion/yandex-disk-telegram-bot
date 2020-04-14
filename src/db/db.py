from sqlalchemy.pool import NullPool

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(
    engine_options={
        # pooling will be disabled until that
        # https://stackoverflow.com/questions/61197228/flask-gunicorn-gevent-sqlalchemy-postgresql-too-many-connections
        # will be resolved
        "poolclass": NullPool
    }
)
