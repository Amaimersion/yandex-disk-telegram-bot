from flask import redirect, url_for

from src.blueprints._common.utils import absolute_url_for
from src.blueprints.legal import legal_blueprint as bp


@bp.route("/privacy-policy")
def privacy_policy():
    return redirect(
        absolute_url_for(
            "static",
            filename="legal/privacy_policy.txt"
        )
    )


@bp.route("/terms-and-conditions")
def terms_and_conditions():
    return redirect(
        absolute_url_for(
            "static",
            filename="legal/terms_and_conditions.txt"
        )
    )
