"""
Runs RQ worker.
"""

import redis
from rq import Worker, Queue, Connection

from src.app import create_app


def main():
    app = create_app()
    redis_url = app.config.get("REDIS_URL")

    if not redis_url:
        raise Exception("Redis URL is not specified")

    connection = redis.from_url(redis_url)
    listen = ["default"]

    with Connection(connection):
        # we should bind Flask app context
        # to worker context in order worker
        # have access to valid `current_app`.
        # It will be not actual app that is
        # currently being running, but app
        # with same ENV configuration
        with app.app_context():
            worker = Worker(
                map(Queue, listen)
            )

            worker.work()


if __name__ == "__main__":
    main()
