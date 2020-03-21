from flask import (
    Blueprint
)


bp = Blueprint(
    "telegram_bot",
    __name__
)


@bp.route("/")
def index():
    return "Hello!"
