from datetime import datetime, timezone


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
