"""
Runs RQ worker.
"""

import redis
from rq import Worker, Queue, Connection

from src.app import create_app


def main():
    """
    Creates single RQ worker and runs it.

    NOTE:
    App context. Separate one will be created
    (not actual app that serves requests) and
    will be pushed to the worker. You will have
    access to the valid `current_app` and `g`,
    BUT every time when worker will perform some
    new job, this new job will have access to clean
    `current_app` and `g`, not to the old ones
    (from old jobs or actual server application).
    It is because every new job is a fork of clean
    app context that was created at the start of worker.
    So, you can safely use `g` inside of yours jobs,
    because `g` from first job will not intersects with
    `g` from second job, BUT you will need initialize
    `g` every time at a job start, because every time
    you will get clean `g`. `current_app` can be used,
    for example, to read ENV configuration of the app.

    NOTE:
    Request context. It will be not available.
    If needed, you should push it manually.

    NOTE:
    Function that was passed to background task will be
    imported (like usual `import`) after fork.
    """
    app = create_app()
    redis_url = app.config.get("REDIS_URL")

    if not redis_url:
        raise Exception("Redis URL is not specified")

    connection = redis.from_url(redis_url)
    listen = ["default"]

    with Connection(connection):
        with app.app_context():
            worker = Worker(
                map(Queue, listen)
            )

            worker.work()


if __name__ == "__main__":
    main()
