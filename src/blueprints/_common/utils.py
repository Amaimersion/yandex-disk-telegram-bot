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


def get_current_iso_datetime(sep="T", timespec="seconds") -> str:
    """
    See https://docs.python.org/3.8/library/datetime.html#datetime.datetime.isoformat # noqa
    """
    return datetime.now(timezone.utc).isoformat(sep, timespec)


def convert_iso_datetime(date_string: str) -> dict:
    """
    :returns:
    Pretty-print information about ISO 8601 `date_string`.
    """
    value = datetime.fromisoformat(date_string)
    value_date = value.strftime("%d.%m.%Y")
    value_time = value.strftime("%H:%M:%S")
    value_timezone = value.strftime("%Z")

    return {
        "date": value_date,
        "time": value_time,
        "timezone": value_timezone
    }


def bytes_to_human_unit(
    bytes_count: int,
    factor: float,
    suffix: str
) -> str:
    """
    Converts bytes to human readable string.

    - function source: https://stackoverflow.com/a/1094933/8445442
    - https://en.wikipedia.org/wiki/Binary_prefix
    - https://man7.org/linux/man-pages/man7/units.7.html

    :param bytes_count:
    Count of bytes to convert.
    :param factor:
    Use `1024.0` for binary and `1000.0` for decimal.
    :param suffix:
    Use `iB` for binary and `B` for decimal.
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(bytes_count) < factor:
            return "%3.1f %s%s" % (bytes_count, unit, suffix)

        bytes_count /= factor

    return "%.1f %s%s" % (bytes_count, "Y", suffix)


def bytes_to_human_binary(bytes_count: int) -> str:
    """
    Bytes -> binary representation.
    """
    return bytes_to_human_unit(bytes_count, 1024.0, "iB")


def bytes_to_human_decimal(bytes_count: int) -> str:
    """
    Bytes -> decimal representation.
    """
    return bytes_to_human_unit(bytes_count, 1000.0, "B")


def get_str_bytes_length(value: str) -> int:
    """
    - source: https://stackoverflow.com/a/30686735/8445442
    """
    return len(value.encode("utf-8"))
