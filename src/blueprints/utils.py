from datetime import datetime, timezone

from flask import (
    current_app,
    url_for
)


def absolute_url_for(endpoint: str, **kwargs) -> str:
    """
    Implements Flask `url_for`, but by default
    creates absolute URL (`_external` and `_scheme`) with
    `PREFERRED_URL_SCHEME` scheme.

    - you can specify these parameters to change behavior.

    https://flask.palletsprojects.com/en/1.1.x/api/#flask.url_for
    """
    if ("_external" not in kwargs):
        kwargs["_external"] = True

    if ("_scheme" not in kwargs):
        kwargs["_scheme"] = current_app.config["PREFERRED_URL_SCHEME"]

    return url_for(endpoint, **kwargs)


def get_current_datetime() -> dict:
    """
    :returns: Information about current date and time.
    """
    current_datetime = datetime.now(timezone.utc)
    current_date = current_datetime.strftime("%d.%m.%Y")
    current_time = current_datetime.strftime("%H:%M:%S")
    current_timezone = current_datetime.strftime("%Z")

    return {
        "date": current_date,
        "time": current_time,
        "timezone": current_timezone
    }
