"""
Flask extensions that used by the app.
They already preconfigured and should be just
initialized by the app. Optionally, at initialization
stage you can provide additional configuration.
These extensions extracted in separate module in order
to avoid circular imports.
"""

from typing import (
    Union
)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel
from sqlalchemy.pool import NullPool
import redis
from rq import Queue as RQ


# Database

db = SQLAlchemy(
    engine_options={
        # pooling will be disabled until that
        # https://stackoverflow.com/questions/61197228/flask-gunicorn-gevent-sqlalchemy-postgresql-too-many-connections
        # will be resolved
        "poolclass": NullPool
    }
)


# Migration

migrate = Migrate(
    compare_type=True,
    render_as_batch=True
)


# i18n

babel = Babel()


# Redis

class FlaskRedis:
    def __init__(self):
        self._redis_client = None

    def __getattr__(self, name):
        return getattr(self._redis_client, name)

    def __getitem__(self, name):
        return self._redis_client[name]

    def __setitem__(self, name, value):
        self._redis_client[name] = value

    def __delitem__(self, name):
        del self._redis_client[name]

    @property
    def connection(self) -> redis.Redis:
        return self._redis_client

    @property
    def is_enabled(self) -> bool:
        return (self.connection is not None)

    def init_app(self, app: Flask, **kwargs) -> None:
        self._redis_client = None
        redis_server_url = app.config.get("REDIS_URL")

        if not redis_server_url:
            return

        self._redis_client = redis.from_url(
            redis_server_url,
            decode_responses=True,
            **kwargs
        )


redis_client: Union[redis.Redis, FlaskRedis] = FlaskRedis()


# Redis Queue

class RedisQueue:
    def __init__(self):
        self._queue = None

    def __getattr__(self, name):
        return getattr(self._queue, name)

    def __getitem__(self, name):
        return self._queue[name]

    def __setitem__(self, name, value):
        self._queue[name] = value

    def __delitem__(self, name):
        del self._queue[name]

    @property
    def is_enabled(self) -> bool:
        return (self._queue is not None)

    def init_app(
        self,
        app: Flask,
        redis_connection: redis.Redis,
        **kwargs
    ) -> None:
        enabled = app.config.get("RUNTIME_RQ_ENABLED")

        if not enabled:
            return

        self._queue = RQ(
            connection=redis_connection,
            name="default"
        )


task_queue: Union[RQ, RedisQueue] = RedisQueue()
