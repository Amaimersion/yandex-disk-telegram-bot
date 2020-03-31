from flask import make_response


def error():
    """
    Creates error response for Telegram Webhook.
    """
    return make_response((
        {
            "ok": False,
            "error_code": 400
        },
        200
    ))


def success():
    """
    Creates success response for Telegram Webhook.
    """
    return make_response((
        {
            "ok": True
        },
        200
    ))
