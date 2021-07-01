from typing import Union, Callable

from flask import (
    g,
    has_app_context
)


class RQTaskPrepareData:
    """
    See `prepare_task` documentation.
    """
    def __init__(self):
        self.g_data = {}


def prepare_task() -> RQTaskPrepareData:
    """
    Prepares data to run background task.

    It creates copy of current request data
    (`g`, for example). That data will be available
    in background task.

    NOTE:
    this function should be called inside of application
    context and request context, i.e. inside of current request.
    """
    data = RQTaskPrepareData()

    if has_app_context():
        for key in g:
            data.g_data[key] = g.get(key)

    return data


def setup_task(prepare_data: RQTaskPrepareData) -> None:
    """
    Sets up data that was created using `prepare_task`.

    NOTE:
    this function should be called inside of background
    task.
    """
    if has_app_context():
        for key, value in prepare_data.g_data.items():
            setattr(g, key, value)


def run_task(
    f: Callable,
    prepare_data: Union[RQTaskPrepareData, None] = None,
    args: tuple = (),
    kwargs: dict = {}
) -> None:
    """
    Runs background task.

    NOTE:
    you should pass this function to task queue.

    :param f:
    Function that will be called from background task.
    :param prepare_data:
    If you want to keep current request data (`g`, for example),
    then create special data with `prepare_task()`.
    :param args:
    `*args` for `f`.
    :param kwargs:
    `**kwargs` for `f`.
    """
    if prepare_data:
        setup_task(prepare_data)

    f(*args, **kwargs)
